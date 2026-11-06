"""Export a registered native UI/API library into a NEW review snapshot."""
import hashlib
import json
from pathlib import Path
import re
from .config import read_json, write_new, contained

MEDIA={'.png','.jpg','.jpeg','.webp','.mp4','.mov','.webm','.wav','.mp3','.flac','.glb','.gltf','.fbx'}


def export(cfg, source_catalog, out):
    source_catalog=Path(source_catalog).expanduser().resolve();out=Path(out).expanduser().absolute()
    if out.exists():raise FileExistsError('Use a new snapshot directory; existing sources are preserved')
    source=read_json(source_catalog)
    if not isinstance(source,list):raise ValueError('Source catalog must be a list of registered model/function/API/UI entries')
    replacements={str(source_catalog.parent.parent):'${LEGACY_MANAGEMENT_ROOT}',source_catalog.parent.parent.as_posix():'${LEGACY_MANAGEMENT_ROOT}'}
    if cfg.comfy:replacements.update({str(cfg.comfy):'${COMFYUI_ROOT}',cfg.comfy.as_posix():'${COMFYUI_ROOT}'})
    rows=[];planned=[]
    for row in source:
        model,function=row['model'],row['function']
        for fragment in [model,function]:
            if Path(fragment).is_absolute() or '..' in Path(fragment.replace('\\','/')).parts or ':' in fragment:raise ValueError('Unsafe source catalog function')
        media={}
        def scrub(v):
            if isinstance(v,dict):return {k:scrub(x) for k,x in v.items() if k not in {'nodeOutputs','last_outputs','workflowRendererVersion'}}
            if isinstance(v,list):return [scrub(x) for x in v]
            if not isinstance(v,str):return v
            if v.startswith('data:'):return ''
            if v.startswith(('{','[')):
                try:return json.dumps(scrub(json.loads(v)),ensure_ascii=False)
                except ValueError:pass
            ext=Path(v.split('?',1)[0]).suffix.lower()
            if ext in MEDIA and len(v)<500 and not v.startswith('http'):
                media.setdefault(v,f'UPLOAD_{len(media)+1}{ext}');return media[v]
            for old,new in sorted(replacements.items(),key=lambda x:-len(x[0])):v=v.replace(old,new)
            if re.search(r'[A-Za-z]:[\\/]|/Users/|/home/[^/]+/',v):
                v=re.sub(r'[A-Za-z]:[\\/][^\s`<>"\']+','${LOCAL_PATH}',v)
            return v
        api_source=Path(row['api']);ui_source=Path(row['workflow'])
        if not api_source.is_file() or not ui_source.is_file():raise FileNotFoundError('Source registered UI/API is missing')
        graph=scrub(read_json(api_source));ui=scrub(read_json(ui_source))
        api_rel=f'workflows/api/{model}/{function}.api.json';ui_rel=f'workflows/ui/{model}/{function}.json'
        for rel,value in [(api_rel,graph),(ui_rel,ui)]:
            contained(out/rel,out);planned.append((out/rel,value))
        rows.append({'model':model,'function':function,'api':api_rel,'workflow':ui_rel,'legacy_functions':row.get('legacy_functions',[]),
                     'weights':row.get('weights',[]),'content_label':row.get('content_label'),'required_uploads':sorted(media.values()),
                     'source_api_sha256':hashlib.sha256(api_source.read_bytes()).hexdigest(),
                     'validation':{'scope':'imported-record; not rerun','label':row.get('status','not provided'),'current_install_tested':False}})
    out.mkdir(parents=True)
    for p,value in planned:write_new(p,value)
    write_new(out/'workflows/catalog.json',rows)
    write_new(out/'export-summary.json',{'workflows':len(rows),'inference_performed':False,'next':'Review paths, model/node metadata, graph semantics and required uploads before promoting this snapshot into the canonical repository.'})
    return {'snapshot':str(out),'workflows':len(rows),'modified_source':False}
