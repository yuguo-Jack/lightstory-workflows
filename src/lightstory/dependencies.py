"""Pinned third-party checkouts. No branch-following, automatic pip or service start."""
from pathlib import Path
import hashlib
import subprocess
import urllib.request
from .config import contained, read_json


def registry(cfg):
    return read_json(cfg.repository / "third_party/dependencies.lock.json")["dependencies"]


def resolve(cfg, id_):
    rows = [r for r in registry(cfg) if r["id"] == id_]
    if len(rows) != 1: raise ValueError("Unknown dependency id")
    return rows[0]


def location(cfg, row):
    return cfg.dependency_path(row["id"]) or contained(cfg.tools / "lightstory/dependencies" / row["id"], cfg.tools)


def run(path, *args):
    p = subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode:
        raise RuntimeError(p.stderr.strip() or "git command failed")
    return p.stdout.strip()


def verify(cfg, row, *, baseline_only=False):
    p = location(cfg, row)
    if row["kind"] == "file":
        f = p / row["file"]
        return f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest() == row["sha256"]
    if not (p / ".git").exists(): return False
    try:
        if run(p, "rev-parse", "HEAD") != row["revision"]: return False
        if baseline_only: return True
        expected = row.get("patched_files", {})
        changed = set(run(p, "diff", "HEAD", "--name-only").splitlines())
        if changed - set(expected): return False
        for name, digest in expected.items():
            f = contained(p / name, p)
            if not f.is_file() or hashlib.sha256(f.read_bytes().replace(b"\r\n", b"\n")).hexdigest() != digest:
                return False
        return True
    except (OSError, RuntimeError, ValueError): return False


def fetch(cfg, id_, *, acknowledge_license=False):
    row = resolve(cfg, id_)
    if row.get("requires_license_ack") and not acknowledge_license:
        raise ValueError("Review upstream terms and pass --acknowledge-license for this external dependency")
    target = location(cfg, row)
    if cfg.dependency_path(id_):
        if not verify(cfg,row): raise ValueError("Configured existing dependency differs from the lock; preserved without download, patch or reset")
        return {"id":id_,"path":str(target),"verified":True,"reused_existing_install":True}
    if target.is_symlink(): raise ValueError("Dependency checkout cannot itself be a symlink")
    if row["kind"] == "file":
        target.mkdir(parents=True, exist_ok=True)
        f = target / row["file"]
        if f.exists():
            if not verify(cfg, row): raise ValueError("Existing dependency differs; preserved")
        else:
            with urllib.request.urlopen(row["url"], timeout=30) as response: data = response.read(8 * 1024**2)
            if hashlib.sha256(data).hexdigest() != row["sha256"]: raise ValueError("Dependency checksum mismatch")
            with f.open("xb") as out: out.write(data)
        return {"id": id_, "path": str(target), "verified": True}
    if target.exists():
        if not verify(cfg, row, baseline_only=True): raise ValueError("Existing checkout is a different version; use a new location or review it manually")
        tracked = run(target, "diff", "HEAD", "--name-only").splitlines()
        allowed = set()
        for patch in row.get("patches", []):
            for line in (cfg.repository / patch["path"]).read_text("utf-8").splitlines():
                if line.startswith("+++ b/"): allowed.add(line[6:])
        if set(tracked) - allowed: raise ValueError("Checkout contains unrelated edits; preserved")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(["git", "clone", "--config", "core.autocrlf=false", "--filter=blob:none", "--no-checkout", "--", row["url"], str(target)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if proc.returncode: raise RuntimeError(proc.stderr.strip())
        if row.get("sparse_paths"): run(target, "sparse-checkout", "set", *row["sparse_paths"])
        run(target, "fetch", "origin", row["revision"])
        run(target, "checkout", "--detach", row["revision"])
    for patch in row.get("patches", []):
        file = contained(cfg.repository / patch["path"], cfg.repository / "third_party/patches")
        if hashlib.sha256(file.read_bytes()).hexdigest() != patch["sha256"]: raise ValueError("Patch changed without updating its lock")
        reverse = subprocess.run(["git", "-C", str(target), "apply", "--reverse", "--check", str(file)], capture_output=True)
        if reverse.returncode == 0: continue
        run(target, "apply", "--check", str(file))
        run(target, "apply", str(file))
    if not verify(cfg, row):
        raise ValueError("Checkout does not match its pinned baseline and patched-file hashes; local edits were preserved")
    return {"id": id_, "path": str(target), "revision": run(target, "rev-parse", "HEAD"), "patches": len(row.get("patches", [])), "verified": True}
