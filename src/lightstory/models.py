"""Explicit public-file acquisition with resumable .part and SHA256 validation."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import urllib.request
from .config import contained, read_json, write_new
from . import workflows


def sha(path, offset=0):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        stream.seek(offset)
        for block in iter(lambda: stream.read(8 * 1024**2), b""):
            digest.update(block)
    return digest.hexdigest()


def registry(cfg):
    return read_json(cfg.repository / "models/weights.lock.json")["weights"]


def selection(cfg, *, ids=None, workflow=None, family=None):
    rows = registry(cfg)
    if ids:
        found = [x for x in rows if x["id"] in ids]
        if len(found) != len(set(ids)):
            raise ValueError("Unknown model id")
        return found
    if workflow or family:
        chosen = [workflows.resolve(cfg, workflow)] if workflow else [x for x in workflows.catalog(cfg) if x["model"].casefold() == family.casefold()]
        if not chosen:
            raise ValueError("Unknown model family")
        names = set()
        for row in chosen:
            graph = read_json(workflows.api(cfg, row))
            def collect(v):
                if isinstance(v, dict):
                    for x in v.values(): collect(x)
                elif isinstance(v, list):
                    for x in v: collect(x)
                elif isinstance(v, str):
                    names.add(Path(v.replace("\\", "/")).name)
            collect(graph)
            names.update(Path(x.replace("\\", "/")).name for x in row.get("weights", []))
        found = [x for x in rows if Path(x["relative_path"]).name in names]
        if any(x["model"] == "SkinTokens" for x in chosen):
            found += [x for x in rows if x["relative_path"].startswith("skintokens/") and x not in found]
        return found
    return rows


def target(cfg, item):
    if item["target_root"] == "models":
        base = cfg.models
    elif item["target_root"] == "motion_weights":
        tool = cfg.path("motion2mixamorig_root")
        base = tool / "weights" if tool else None
    else:
        raise ValueError("Unknown model destination root")
    if not base:
        raise ValueError(f"Configure destination for {item['target_root']} first")
    return contained(base / item["relative_path"], base)


def inspect(cfg, items, verify=False):
    result = []
    for item in items:
        try:
            p = target(cfg, item)
            exists = p.is_file()
            row = {"id": item["id"], "path": str(p), "present": exists, "expected_size": item.get("size"), "size_matches": exists and (not item.get("size") or p.stat().st_size == item["size"]), "sha256_verified": None}
            if exists and verify:
                row["sha256_verified"] = sha(p) == item["sha256"]
            result.append(row)
        except ValueError as error:
            result.append({"id": item["id"], "present": False, "configuration_error": str(error)})
    return result


def acquire(cfg, item, *, acknowledge_license=False):
    if not acknowledge_license:
        raise ValueError("Read the selected publisher/base-model licence, then pass --acknowledge-license. This flag is the operator's acknowledgement, not a legal eligibility check.")
    p = target(cfg, item)
    if p.exists():
        if sha(p) != item["sha256"]:
            raise ValueError("Existing model differs; preserved without replacement")
        return {"id": item["id"], "verified": True, "downloaded": False}
    if item.get("recipe"):
        source = next(x for x in registry(cfg) if x["id"] == item["source_id"])
        acquire(cfg, source, acknowledge_license=True)
        normalize_next_scene(target(cfg, source), p, source["sha256"], item["sha256"])
        return {"id": item["id"], "verified": True, "derived": True}
    url = item.get("source", "")
    if not url.startswith("https://") or not item.get("sha256"):
        raise ValueError("Missing HTTPS source or pinned SHA256")
    p.parent.mkdir(parents=True, exist_ok=True)
    partial = p.with_name(p.name + ".part")
    if partial.is_symlink():
        raise ValueError("Refusing a linked partial file")
    size = partial.stat().st_size if partial.exists() else 0
    # A previous download may have finished before the final rename. Do not ask
    # an HTTP server for bytes beyond EOF, or redownload a verified large file.
    if size and item.get("size") and size >= item["size"]:
        if size != item["size"] or sha(partial) != item["sha256"]:
            raise ValueError("Existing complete/oversized partial differs; preserved for review")
        if p.exists():
            raise FileExistsError("Destination appeared; partial preserved")
        partial.rename(p)
        return {"id": item["id"], "verified": True, "downloaded": False, "recovered_partial": True}
    req = urllib.request.Request(url, headers={"User-Agent": "LightStory/0.1", **({"Range": f"bytes={size}-"} if size else {})})
    with urllib.request.urlopen(req, timeout=60) as response:
        resume = size and response.status == 206
        if resume and not response.headers.get("Content-Range", "").startswith(f"bytes {size}-"):
            raise ValueError("Unexpected HTTP range; partial preserved")
        with partial.open("ab" if resume else "wb") as stream:
            shutil.copyfileobj(response, stream, 8 * 1024**2)
    if item.get("size") and partial.stat().st_size != item["size"]:
        raise ValueError("Download incomplete; partial preserved for retry")
    if sha(partial) != item["sha256"]:
        raise ValueError("SHA256 mismatch; partial preserved, never installed")
    if p.exists():
        raise FileExistsError("Destination appeared during download; partial preserved")
    partial.rename(p)
    return {"id": item["id"], "verified": True, "downloaded": True}


def normalize_next_scene(source, destination, expected_source, expected_destination=None):
    source, destination = Path(source), Path(destination)
    if sha(source) != expected_source:
        raise ValueError("Source checksum differs")
    if destination.exists():
        raise FileExistsError(destination)
    with source.open("rb") as stream:
        header_size = struct.unpack("<Q", stream.read(8))[0]
        if header_size > 16 * 1024**2:
            raise ValueError("Unexpected safetensors header length")
        header = json.loads(stream.read(header_size))
        converted = {}
        for name, tensor in header.items():
            if name == "__metadata__": continue
            new = name.removeprefix("diffusion_model.")
            if new in converted: raise ValueError("Tensor name collision")
            converted[new] = tensor
        converted["__metadata__"] = {**header.get("__metadata__", {}), "source_sha256": expected_source, "conversion": "strip diffusion_model. prefix only; tensor payload unchanged"}
        body = json.dumps(converted, separators=(",", ":")).encode("utf-8")
        body += b" " * (-len(body) % 8)
        temporary = destination.with_name(destination.name + ".conversion-tmp")
        with temporary.open("xb") as out:
            out.write(struct.pack("<Q", len(body))); out.write(body); shutil.copyfileobj(stream, out, 8 * 1024**2)
    if sha(source, 8 + header_size) != sha(temporary, 8 + len(body)):
        raise ValueError("Tensor payload changed; temporary preserved")
    if expected_destination and sha(temporary) != expected_destination:
        raise ValueError("Converted header/checksum differs; temporary preserved")
    temporary.rename(destination)
    return {"tensor_count": len(converted) - 1, "payload_identical": True, "sha256": sha(destination)}
