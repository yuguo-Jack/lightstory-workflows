"""Release and readiness checks with explicit evidence boundaries."""
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
from html.parser import HTMLParser
from urllib.parse import unquote
from .config import read_json
from . import dependencies, models, workflows


def document_links(root):
    """Source-layout links; H3 prefixes use their explicit assembled layout."""
    broken=[];checked=0;installed=0
    class Hrefs(HTMLParser):
        def __init__(self):super().__init__();self.links=[]
        def handle_starttag(self,tag,attrs):
            self.links += [value for key,value in attrs if key=='href' and value]
    for p in root.rglob('*'):
        relative=p.relative_to(root)
        if any(x in {'.git','.local','.lightstory','__pycache__','.hyperframes','node_modules'} for x in relative.parts):continue
        if not p.is_file() or p.suffix not in {'.md','.html'} or p.name in {'task_plan.md','findings.md','progress.md'}:continue
        text=p.read_text('utf-8-sig')
        if p.suffix=='.html':
            parser=Hrefs();parser.feed(text);links=parser.links
        else:links=re.findall(r'\[[^\]]*\]\(([^)]+)\)',text)
        for raw in links:
            link=raw.strip().strip('<>').split(' "',1)[0]
            if not link or link.startswith('#') or re.match(r'[A-Za-z][\w+.-]*:',link):continue
            link=unquote(link.split('#',1)[0].split('?',1)[0])
            if not link:continue
            if relative.parent.as_posix()=='third_party/overlays/minimax-h3' and p.name!='README.md':
                if link=='../video-production-workflows/references/h3-skill-adaptation.md':
                    installed+=1;continue
            checked+=1
            target=(p.parent/link).resolve()
            if not target.is_relative_to(root) or not target.exists():broken.append({'source':relative.as_posix(),'target':raw})
    return {'checked':checked,'overlay_install_time_links':installed,'broken':broken}


def validate(cfg):
    root=cfg.repository;errors=[];rows=workflows.catalog(cfg);classes=set();files=0
    required=[f'adapters/comfyui/runtime/{name}.py' for name in ['memory_guard','owned_working_set','inspect_glb','inspect_rigged_glb']]
    required+=['adapters/motion2mixamorig/run.ps1','adapters/motion2mixamorig/restore_materials.py','skills/runtime-map.md','docs/overview.html']
    errors+=['Missing execution/document resource: '+name for name in required if not (root/name).is_file()]
    for row in rows:
        for key in ('api','workflow'):
            p=(root/row[key]).resolve()
            if not p.is_relative_to(root) or not p.is_file():errors.append('Missing/outside workflow: '+row[key]);continue
            try:value=read_json(p)
            except ValueError:errors.append('Invalid JSON: '+str(p));continue
            files+=1
            if key=='api':
                if not value or not all(isinstance(x,dict) and 'class_type' in x and isinstance(x.get('inputs'),dict) for x in value.values()):errors.append('Invalid API graph: '+row[key])
                classes.update(x['class_type'] for x in value.values())
                for n in value.values():
                    for v in n['inputs'].values():
                        if isinstance(v,list) and len(v)==2 and isinstance(v[0],str) and isinstance(v[1],int) and v[0] not in value:errors.append('Dangling API link: '+row[key])
    req=read_json(root/'workflows/node-providers.json')
    errors += ['Missing node provider: '+x for x in classes if x not in req]
    weightrows=models.registry(cfg);known={Path(x['relative_path']).name for x in weightrows}
    errors += ['Missing model provenance: '+x for x in read_json(root/'workflows/required-model-files.json') if Path(x).name not in known]
    for x in weightrows:
        if not re.fullmatch('[0-9a-f]{64}',x.get('sha256') or ''):errors.append('Invalid model checksum: '+x['id'])
        if Path(x['relative_path']).is_absolute() or '..' in Path(x['relative_path']).parts:errors.append('Unsafe model destination: '+x['id'])
    for dep in dependencies.registry(cfg):
        if dep['kind']=='git' and not re.fullmatch('[0-9a-f]{40}',dep.get('revision','')):errors.append('Unpinned dependency: '+dep['id'])
        for patch in dep.get('patches',[]):
            p=root/patch['path']
            if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=patch['sha256']:errors.append('Patch checksum mismatch: '+patch['path'])
    excluded={'.git','.local','.lightstory','__pycache__','.hyperframes','node_modules'}
    sensitive=[];code=0
    for p in root.rglob('*'):
        if not p.is_file() or any(x in excluded or x.endswith('.egg-info') for x in p.relative_to(root).parts):continue
        if p.name in {'task_plan.md','findings.md','progress.md'} or p.name.startswith('local') and p.parent.name=='config':continue
        if p.suffix=='.py':
            code+=1
            try:ast.parse(p.read_text('utf-8-sig'),filename=str(p))
            except SyntaxError as e:errors.append('Python parse: '+str(e))
        # Exactly one reviewed, public product film; all other production media stay private.
        public_film=p.relative_to(root).as_posix()=='docs/film/lightstory-intro.mp4'
        if p.suffix in {'.safetensors','.ckpt','.pkl','.pt','.blend','.fbx','.glb','.mp4','.wav','.dmp'} and not public_film:sensitive.append(p.relative_to(root).as_posix())
        if p.suffix.lower() in {'.md','.json','.py','.ps1','.yml','.yaml','.toml','.txt','.html','.patch'}:
            text=p.read_text('utf-8-sig',errors='replace')
            pattern = r'C:[\\/]+Users[\\/]+Administrator|hf_[A-Za-z0-9]{25,}|gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{20,}|' + 'xsec_' + 'token='
            host_path=str(root).replace('\\','/').casefold()
            normalized=text.replace('\\\\','/').replace('\\','/').casefold()
            if re.search(pattern,text,re.I) or host_path in normalized:sensitive.append(p.relative_to(root).as_posix())
    errors+=['Review public-file privacy/content: '+x for x in sensitive]
    links=document_links(root)
    errors+=['Broken document link: '+x['source']+' -> '+x['target'] for x in links['broken']]
    return {'passed':not errors,'errors':errors,'workflows':len(rows),'UI_API_JSON_checked':files,'required_node_types':len(classes),'model_records':len(weightrows),'python_files_parsed':code,'document_links_checked':links['checked'],'overlay_install_time_links':links['overlay_install_time_links'],'scope':'Static portable package checks only; no model inference, editor launch, provider login or paid operation.'}


def doctor(cfg, *, online=False, workflow=None):
    row=workflows.resolve(cfg,workflow) if workflow else None
    result={'configuration':cfg.summary(),'python':sys.version.split()[0],
            'executables':{x:{'path':cfg.executable(x,x if x in {'ffmpeg','ffprobe','git'} else None),'present':bool(cfg.executable(x,x if x in {'ffmpeg','ffprobe','git'} else None) and Path(cfg.executable(x,x if x in {'ffmpeg','ffprobe','git'} else None)).is_file())} for x in ['git','ffmpeg','ffprobe','blender','comfyui_python','unreal_editor','motion_python']},
            'dependencies':[{"id":x['id'],"pinned_checkout_present":dependencies.verify(cfg,x)} for x in dependencies.registry(cfg)],
            'native_plugins':{'game_studio':'discover in your agent client; not implied by files','unreal_mcp':'requires editor project and a successful live read-only call','capcut':'requires this client/account integration or the documented local editing route'},'gpu_inference_tested':False}
    if online:
        status=workflows.status(cfg);result['comfyui']=status
        if status.get('service_ready'):
            info=workflows.http(cfg,'/object_info')
            classes=read_json(cfg.repository/'workflows/node-requirements.json')
            needed=classes[row['model']+'/'+row['function']] if row else sorted({x for v in classes.values() for x in v})
            result['missing_node_types']=[x for x in needed if x not in info]
    if row:
        result['models']=models.inspect(cfg,models.selection(cfg,workflow=workflow))
        result['required_media_uploads']=row.get('required_uploads',[])
    return result
