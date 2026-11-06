"""Portable read-only host probe. Does not launch an editor or inference."""
from pathlib import Path
import argparse,json,sys
for parent in Path(__file__).resolve().parents:
    if (parent / "src/lightstory/cli.py").is_file():
        sys.path.insert(0,str(parent / "src"));break
from lightstory.config import Config,write_new
from lightstory.audit import doctor
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--config");p.add_argument("--output");p.add_argument("--project");p.add_argument("--engine-root");p.add_argument("--online",action="store_true");a=p.parse_args()
    cfg=Config.load(a.config)
    if a.engine_root:cfg.data.setdefault("executables",{})["unreal_editor"]=str(Path(a.engine_root)/"Engine/Binaries/Win64/UnrealEditor.exe")
    result=doctor(cfg,online=a.online)
    if a.project:result["project"]={"path":str(Path(a.project).absolute()),"present":Path(a.project).exists(),"executed":False}
    if a.output:write_new(a.output,result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
