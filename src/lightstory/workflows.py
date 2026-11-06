"""Read portable workflows and prepare requests; never submit GPU work."""
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import urllib.request
import uuid
from .config import contained, read_json, write_new


def catalog(cfg):
    return read_json(cfg.repository / "workflows/catalog.json")


def resolve(cfg, name):
    name = name.replace("\\", "/").casefold()
    rows = [r for r in catalog(cfg) if any((r["model"] + "/" + n).casefold() == name for n in [r["function"], *r.get("legacy_functions", [])])]
    if len(rows) != 1:
        raise ValueError("Use the exact model/function name from workflows list")
    return rows[0]


def api(cfg, row):
    return contained(cfg.repository / row["api"], cfg.repository / "workflows/api")


def http(cfg, route, data=None):
    req = urllib.request.Request(cfg.url + route, data=None if data is None else json.dumps(data).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as response:
        body = response.read()
        return json.loads(body) if body else {}


def status(cfg):
    result = cfg.summary()
    try:
        stats, queue = http(cfg, "/system_stats"), http(cfg, "/queue")
        result.update(service_ready=True, system=stats.get("system"), devices=stats.get("devices"),
                      running_prompt_ids=[x[1] for x in queue.get("queue_running", [])], pending=len(queue.get("queue_pending", [])))
    except (OSError, ValueError) as error:
        result.update(service_ready=False, error=str(error))
    return result


def prepare(cfg, name, *, overrides=None, prefix=None, out=None):
    row = resolve(cfg, name)
    source = api(cfg, row)
    graph = copy.deepcopy(read_json(source))
    changes = overrides or {}
    if not isinstance(changes, dict):
        raise ValueError("Overrides must be node_id -> input object")
    for identifier, values in changes.items():
        if identifier not in graph or not isinstance(values, dict):
            raise ValueError(f"Unknown node or invalid override: {identifier}")
        for key, value in values.items():
            if key not in graph[identifier]["inputs"]:
                raise ValueError(f"Unknown input {identifier}.{key}")
            graph[identifier]["inputs"][key] = json.dumps(value, ensure_ascii=False) if key == "timeline_data" and isinstance(value, dict) else value
    job = uuid.uuid4().hex[:12]
    prefix = (prefix or "jobs/" + job).replace("\\", "/")
    parts = PurePosixPath(prefix)
    if not prefix or parts.is_absolute() or ".." in parts.parts or ":" in prefix:
        raise ValueError("Output prefix must be relative to native ComfyUI output")
    for identifier, node in graph.items():
        values = node["inputs"]
        if "filename_prefix" in values:
            values["filename_prefix"] = prefix + "/" + node["class_type"] + "_" + identifier
        if node["class_type"] == "MiniMaxH3Director" and "cache_name" not in changes.get(identifier, {}):
            values["cache_name"] = "job_" + job
    text = json.dumps(graph, ensure_ascii=False, indent=2) + "\n"
    if "UPLOAD_" in text:
        raise ValueError("Unbound media placeholders remain. Upload/select your own inputs and override every required media input, including encoded H3 Group/timeline data.")
    target = Path(out).expanduser() if out else cfg.runtime / "jobs" / job / "request.api.json"
    if not target.is_absolute():
        raise ValueError("--out must be absolute")
    target = target.resolve()
    protected = [cfg.repository / "workflows", cfg.repository / "skills", cfg.repository / "third_party"]
    if cfg.ui_root:
        protected.append(cfg.ui_root)
    if any(target == p.resolve() or target.is_relative_to(p.resolve()) for p in protected):
        raise ValueError("Request output overlaps a protected workflow/Skill/dependency directory")
    receipt = target.with_suffix(".prepared.json")
    if target.exists() or receipt.exists():
        raise FileExistsError("Prepared request or receipt already exists")
    write_new(target, graph)
    result = {"workflow": row["model"] + "/" + row["function"], "canonical_api": str(source),
              "canonical_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "request": str(target),
              "request_sha256": hashlib.sha256(target.read_bytes()).hexdigest(), "overridden_nodes": list(changes),
              "output_prefix": prefix, "submitted": False,
              "note": "Preparation only. Check effective timeline, input roles and live schema before authorized POST /prompt."}
    write_new(receipt, result)
    return result
