"""Reviewable, non-overwriting installations; source checkout stays authoritative."""
from pathlib import Path
import hashlib
import json
import shutil
from .config import contained, read_json
from . import dependencies, workflows


def same_tree(a, b):
    if a.is_file() and b.is_file(): return a.read_bytes() == b.read_bytes()
    if not a.is_dir() or not b.is_dir(): return False
    def files(p): return {x.relative_to(p).as_posix(): hashlib.sha256(x.read_bytes()).hexdigest() for x in p.rglob("*") if x.is_file() and "__pycache__" not in x.parts}
    return files(a) == files(b)


def install_plan(pairs):
    result = []
    for source, target in pairs:
        source, target = Path(source).resolve(), Path(target).absolute()
        if not source.exists(): raise FileNotFoundError(source)
        present = target.exists() or target.is_symlink()
        equivalent = present and (target.resolve() == source or same_tree(source, target))
        result.append({"source": str(source), "target": str(target), "action": "keep" if equivalent else "conflict" if present else "link"})
    return result


def execute(plan, *, apply=False, copy=False):
    if any(x["action"] == "conflict" for x in plan):
        return {"applied": False, "conflicts": [x for x in plan if x["action"] == "conflict"], "plan": plan}
    if apply:
        for x in plan:
            if x["action"] == "keep": continue
            src, dst = Path(x["source"]), Path(x["target"])
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists() or dst.is_symlink(): raise FileExistsError("Destination appeared; refusing overwrite")
            if copy:
                if src.is_dir(): shutil.copytree(src, dst)
                else: shutil.copy2(src, dst)
            else:
                dst.symlink_to(src, target_is_directory=src.is_dir())
    return {"applied": apply, "mode": "copy" if copy else "symlink", "plan": plan}


def skill_sources(cfg, upstream=False, materialize=False, copy=False):
    sources = [p for p in (cfg.repository / "skills").iterdir() if p.is_dir() and (p / "SKILL.md").is_file()]
    sources += [p for p in (cfg.repository / "third_party/skills/blender-skills").iterdir() if p.is_dir() and (p / "SKILL.md").is_file()]
    if upstream:
        dep = dependencies.resolve(cfg, "minimax-h3-skills")
        base = dependencies.location(cfg, dep)
        if not dependencies.verify(cfg, dep): raise ValueError("Fetch the pinned minimax-h3-skills dependency first")
        stages = cfg.state_root / "skills"
        # A coherent sibling layout preserves the upstream-to-local adaptation links.
        for source in [*sources, cfg.repository / 'skills/runtime-map.md']:
            dest = stages / source.name
            if materialize:
                result = execute(install_plan([(source, dest)]), apply=True, copy=copy)
                if result.get("conflicts"): raise ValueError("Skill staging collision")
        for overlay in (cfg.repository / "third_party/overlays/minimax-h3").glob("*.md"):
            if overlay.name == "README.md": continue
            name = overlay.stem
            upstream_name = "music-video-subtitle-generator" if name == "mv-subtitle-skill-confirmed" else name
            original = base / "skills" / upstream_name
            if not (original / "SKILL.md").is_file(): raise FileNotFoundError(original / "SKILL.md")
            dest = stages / name
            if materialize:
                if dest.is_symlink(): raise ValueError("Unexpected link for an assembled upstream Skill")
                original_text = (original / "SKILL.md").read_text("utf-8-sig")
                if not original_text.startswith("---"): raise ValueError("Invalid upstream Skill frontmatter")
                header=original_text.split("---",2)[1].splitlines()
                begin=next((i for i,line in enumerate(header) if line.startswith('description:')),None)
                if begin is None:raise ValueError('Upstream Skill has no description')
                end=next((i for i in range(begin+1,len(header)) if header[i] and not header[i][0].isspace() and ':' in header[i] and not header[i].startswith('#')),len(header))
                description='\n'.join(header[begin:end]).rstrip()
                body = original_text.split("---", 2)[2].lstrip()
                prefix = overlay.read_text("utf-8")
                metadata = f'---\nname: {upstream_name}\n{description}\nmetadata:\n  upstream: "MiniMax-AI/MiniMax-H3"\n  revision: "{dep["revision"]}"\n---\n\n'
                expected = metadata + prefix + "\n\n" + body
                if dest.exists():
                    if (dest / "SKILL.md").read_text("utf-8") != expected: raise ValueError("Existing upstream adaptation changed; preserved")
                else:
                    shutil.copytree(original, dest)
                    (dest / "SKILL.md").write_text(expected, "utf-8")
            sources.append(dest)
    return sources


def skills(cfg, *, agent="codex", target=None, upstream=False, apply=False, copy=False):
    sources = skill_sources(cfg, upstream, materialize=apply, copy=copy)
    root = Path(target).expanduser().absolute() if target else Path.home() / (".codex" if agent == "codex" else ".claude") / "skills"
    if upstream and not apply:
        # Assembled source paths do not exist in a pristine dry-run; describe them without creating them.
        result=[]
        for p in sources:
            dst=root/p.name
            result += install_plan([(p,dst)]) if p.exists() else [{"source":str(p),"target":str(dst),"action":"assemble-then-link" if not dst.exists() else "review-existing"}]
        result += install_plan([(cfg.repository / 'skills/runtime-map.md', root / 'runtime-map.md')])
        return {"applied":False,"plan":result}
    return execute(install_plan([(p, root / p.name) for p in sources] + [(cfg.repository / 'skills/runtime-map.md', root / 'runtime-map.md')]), apply=apply, copy=copy)


def ui(cfg, *, target=None, apply=False):
    root = Path(target).expanduser().absolute() if target else cfg.ui_library
    if not root: raise ValueError("Configure comfyui_root/workflow_root or pass --target")
    pairs=[]
    for row in workflows.catalog(cfg):
        source=contained(cfg.repository/row["workflow"],cfg.repository/'workflows/ui')
        destination=(root/row['model']/(row['function']+'.json')).absolute()
        relative=destination.relative_to(root.absolute())
        if '..' in relative.parts or not destination.parent.resolve().is_relative_to(root.resolve()):
            raise ValueError('Workflow destination parent escapes the native library')
        # The leaf may intentionally link back to this checkout after migration.
        # Resolve the parent for containment, not the linked file itself.
        pairs.append((source,destination))
    result=execute(install_plan(pairs), apply=apply, copy=True)
    if apply and not result.get('conflicts'):
        record=cfg.state_root/'installed/workflows.json';record.parent.mkdir(parents=True,exist_ok=True)
        data={'schema_version':1,'maintenance_source':str(cfg.repository/'workflows'),'mode':'native editable copies; promote deliberate changes through review',
              'files':[{'source':str(src),'target':str(dst),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest()} for src,dst in pairs]}
        record.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
        result['installed_index']=str(record)
    return result


def nodes(cfg, *, apply=False):
    if not cfg.comfy: raise ValueError("Configure ComfyUI first")
    root=cfg.comfy/'custom_nodes';pairs=[];missing=[]
    for p in (cfg.repository/'adapters/comfyui/nodes').iterdir():
        if p.is_dir():pairs.append((p,root/p.name))
    for dep in dependencies.registry(cfg):
        destination=dep.get('node_directory') or dep.get('node_file')
        if not destination:continue
        if not dependencies.verify(cfg,dep):missing.append(dep['id']);continue
        src=dependencies.location(cfg,dep)
        if dep.get('node_file'):src=src/dep['file']
        pairs.append((src,root/destination))
    skin=next((p for p in pairs if p[1].name=='ComfyUI-SkinTokens-NoBlender'),None)
    if skin and cfg.models:
        file=skin[0]/'local_config.json'
        expected={'models_dir':str(cfg.models/'skintokens'),'allow_download':False}
        if file.exists():
            actual=read_json(file)
            equivalent=(isinstance(actual,dict) and actual.get('allow_download') is False
                        and isinstance(actual.get('models_dir'),str)
                        and Path(actual['models_dir']).expanduser().resolve()==(cfg.models/'skintokens').resolve())
            if not equivalent:raise ValueError('Existing SkinTokens local config differs; preserved')
    result=execute(install_plan(pairs),apply=apply)
    result['not_fetched']=missing
    if apply and not result.get('conflicts') and skin and cfg.models and not file.exists():
        file.write_text(json.dumps(expected,indent=2)+'\n','utf-8')
    return result
