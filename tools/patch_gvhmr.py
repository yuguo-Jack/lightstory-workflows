"""Review/apply only the recorded GVHMR 1.6.1 RTMPose asset-selection fix."""
import argparse
import importlib.metadata
import json
from pathlib import Path
import subprocess

REPLACEMENTS = {
    "cli/demo.py": [
        ('def ensure_assets(camera: str, want_render: bool = True, repo: str | None = None) -> None:',
         'def ensure_assets(camera: str, want_render: bool = True, repo: str | None = None, *, pose2d: str = "vitpose") -> None:'),
        ('need = ["gvhmr", "hmr2", "vitpose", "yolo"] + (["dpvo"] if camera == "dpvo" else [])',
         'need = ["gvhmr", "hmr2", "yolo"] + (["vitpose"] if pose2d == "vitpose" else []) + (["dpvo"] if camera == "dpvo" else [])'),
        ('ensure_assets(cam_name, want_render=(not no_render and mesh == "smpl"))',
         'ensure_assets(cam_name, want_render=(not no_render and mesh == "smpl"), pose2d=cfg.pose2d.name)')],
    "inference/pipelines.py": [
        ('ensure_assets(cam_name, want_render=render, repo=self.model.repo_id)',
         'ensure_assets(cam_name, want_render=render, repo=self.model.repo_id, pose2d=cfg.pose2d.name)')]
}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--python',required=True);p.add_argument('--record-dir',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
    probe=subprocess.run([a.python,'-B','-X','utf8','-c','import importlib.util,importlib.metadata,json; print(json.dumps({"version":importlib.metadata.version("gvhmr"),"root":list(importlib.util.find_spec("gvhmr").submodule_search_locations)[0]}))'],capture_output=True,text=True,encoding='utf-8',check=True)
    data=json.loads(probe.stdout)
    if data['version']!='1.6.1':raise ValueError('Patch only targets gvhmr 1.6.1; inspect a new version instead')
    root=Path(data['root']).resolve();changes=[]
    for rel,rules in REPLACEMENTS.items():
        target=(root/rel).resolve()
        if not target.is_relative_to(root):raise ValueError('Package path escapes root')
        old=target.read_text('utf-8');new=old
        for before,after in rules:
            if after in new and before not in new:continue
            if new.count(before)!=1:raise ValueError('Patch context differs; no changes applied')
            new=new.replace(before,after,1)
        changes.append((rel,target,old,new))
    record=Path(a.record_dir).expanduser().absolute()
    if a.apply:
        record.mkdir(parents=True,exist_ok=True)
        for rel,target,old,new in changes:
            if old==new:continue
            backup=record/(rel.replace('/','__')+'.before')
            with backup.open('x',encoding='utf-8') as f:f.write(old)
            target.write_text(new,'utf-8')
    result={'version':data['version'],'package':str(root),'applied':a.apply,'changed_files':[rel for rel,_,old,new in changes if old!=new],'already_patched':all(old==new for _,_,old,new in changes)}
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
