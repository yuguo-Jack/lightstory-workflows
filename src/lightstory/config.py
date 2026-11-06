"""One configuration for every adapter. Merely loading it creates no folders."""
from __future__ import annotations
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit

REPO = Path(__file__).resolve().parents[2]


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        if default is not None:
            return default
        raise


def write_new(path, value):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    return p


def contained(path, root):
    p, r = Path(path).resolve(), Path(root).resolve()
    if p == r or not p.is_relative_to(r):
        raise ValueError(f"Expected a child of {r}: {p}")
    return p


@dataclass
class Config:
    repository: Path
    file: Path
    data: dict

    @classmethod
    def load(cls, file=None):
        repository = Path(os.environ.get("LIGHTSTORY_ROOT", str(REPO))).expanduser().resolve()
        p = Path(file or os.environ.get("LIGHTSTORY_CONFIG", repository / "config/local.json")).expanduser().resolve()
        data = read_json(p, {})
        if not isinstance(data, dict):
            raise ValueError("Configuration must be a JSON object")
        return cls(repository, p, data)

    def path(self, key, default=None):
        raw = self.data.get("paths", {}).get(key, default)
        return self.resolve_path(raw, "paths." + key)

    def resolve_path(self, raw, label="path"):
        if raw is None or raw == "":
            return None
        text = str(raw).replace("${REPO}", str(self.repository)).replace("${HOME}", str(Path.home()))
        text = os.path.expandvars(text)
        if re.search(r"\$\{[^}]+\}", text):
            raise ValueError(f"Unresolved variable in {label}: {raw}")
        p = Path(text).expanduser()
        return (self.file.parent / p).resolve() if not p.is_absolute() else p.resolve()

    def dependency_path(self, identifier):
        return self.resolve_path(self.data.get("dependency_paths", {}).get(identifier), "dependency_paths." + identifier)

    @property
    def ui_library(self):
        if not self.ui_root: return None
        namespace = self.data.get("installation", {}).get("workflow_namespace", "LightStory")
        if not isinstance(namespace,str) or namespace in {'.','..'} or any(x in namespace for x in '/\\:'):
            raise ValueError("workflow_namespace must be an empty or single folder name")
        return self.ui_root / namespace if namespace else self.ui_root

    @property
    def state_root(self):
        return self.path("state_root", "${REPO}/.lightstory")

    @property
    def runtime(self):
        return self.state_root / "runtime"

    @property
    def projects(self):
        return self.path("projects_root", "${HOME}/LightStoryProjects")

    @property
    def comfy(self):
        return self.path("comfyui_root")

    @property
    def models(self):
        return self.path("models_root") or (self.comfy / "models" if self.comfy else None)

    @property
    def inputs(self):
        return self.path("input_root") or (self.comfy / "input" if self.comfy else None)

    @property
    def outputs(self):
        return self.path("output_root") or (self.comfy / "output" if self.comfy else None)

    @property
    def ui_root(self):
        return self.path("workflow_root") or (self.comfy / "user/default/workflows" if self.comfy else None)

    @property
    def tools(self):
        return self.path("tools_root", "${HOME}/.local/share/lightstory/tools")

    def executable(self, name, default=None):
        raw = self.data.get("executables", {}).get(name, default)
        if not raw:
            return None
        return shutil.which(str(raw)) or str(Path(str(raw)).expanduser())

    @property
    def url(self):
        value = self.data.get("services", {}).get("comfyui_url", "http://127.0.0.1:8188").rstrip("/")
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("Use a plain http(s) ComfyUI URL without credentials, query or fragment")
        if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("This local adapter only accepts loopback ComfyUI endpoints")
        return value

    def summary(self):
        return {"configured": self.file.is_file(), "configuration": str(self.file), "repository": str(self.repository),
                "state_root": str(self.state_root), "projects_root": str(self.projects), "comfyui_root": str(self.comfy) if self.comfy else None,
                "models_root": str(self.models) if self.models else None, "workflow_root": str(self.ui_root) if self.ui_root else None,
                "input_root": str(self.inputs) if self.inputs else None, "output_root": str(self.outputs) if self.outputs else None,
                "model_cache_root": str(self.path('model_cache_root')) if self.path('model_cache_root') else None,
                "history_root": str(self.path('history_root') or self.state_root/'host-history'),
                "motion2mixamorig_root": str(self.path('motion2mixamorig_root')) if self.path('motion2mixamorig_root') else None,
                "workflow_library": str(self.ui_library) if self.ui_library else None,
                "tools_root": str(self.tools), "comfyui_url": self.url}
