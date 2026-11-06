"""Small host CLI: explicit plans, no implicit model inference or publication."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from .config import Config, read_json, write_new
from . import __version__, audit, dependencies, install, models, runtime, workflows


def parser():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config');p.add_argument('--version',action='version',version=__version__)
    sub=p.add_subparsers(dest='command',required=True)
    conf=sub.add_parser('config');cs=conf.add_subparsers(dest='action',required=True);ci=cs.add_parser('init');ci.add_argument('--template',choices=['windows','posix'],default='windows' if os.name=='nt' else 'posix');ci.add_argument('--out')
    sub.add_parser('paths');sub.add_parser('validate')
    d=sub.add_parser('doctor');d.add_argument('--online',action='store_true');d.add_argument('--workflow')
    w=sub.add_parser('workflows');ws=w.add_subparsers(dest='action',required=True)
    l=ws.add_parser('list');l.add_argument('--model')
    show=ws.add_parser('show');show.add_argument('workflow')
    ws.add_parser('status')
    prep=ws.add_parser('prepare');prep.add_argument('workflow');prep.add_argument('--overrides');prep.add_argument('--prefix');prep.add_argument('--out')
    m=sub.add_parser('models');ms=m.add_subparsers(dest='action',required=True)
    for action in ['plan','check','fetch']:
        item=ms.add_parser(action);item.add_argument('--id',action='append',dest='ids');item.add_argument('--workflow');item.add_argument('--family')
        if action=='check':item.add_argument('--hash',action='store_true')
        if action=='fetch':item.add_argument('--acknowledge-license',action='store_true')
    ds=sub.add_parser('deps').add_subparsers(dest='action',required=True)
    ds.add_parser('list');fetch=ds.add_parser('fetch');fetch.add_argument('id');fetch.add_argument('--acknowledge-license',action='store_true')
    ins=sub.add_parser('install').add_subparsers(dest='action',required=True)
    sk=ins.add_parser('skills');sk.add_argument('--agent',choices=['codex','claude'],default='codex');sk.add_argument('--target');sk.add_argument('--with-upstream',action='store_true');sk.add_argument('--copy',action='store_true');sk.add_argument('--apply',action='store_true')
    ui=ins.add_parser('workflows');ui.add_argument('--target');ui.add_argument('--apply',action='store_true')
    nd=ins.add_parser('nodes');nd.add_argument('--apply',action='store_true')
    rs=sub.add_parser('runtime').add_subparsers(dest='action',required=True)
    start=rs.add_parser('start');start.add_argument('--profile',choices=['Default','Balanced','Conservative','PixalStable'],default='Balanced');start.add_argument('--no-guard',action='store_true');start.add_argument('--apply',action='store_true')
    stop=rs.add_parser('stop');stop.add_argument('--cancel',action='store_true');stop.add_argument('--apply',action='store_true')
    serve=rs.add_parser('serve');serve.add_argument('--port',type=int);serve.add_argument('--with-history',action='store_true')
    proj=sub.add_parser('project').add_subparsers(dest='action',required=True)
    pi=proj.add_parser('init');pi.add_argument('--kind',choices=['game','video'],required=True);pi.add_argument('--name',required=True);pi.add_argument('--path')
    cleanup=sub.add_parser('cleanup');cleanup.add_argument('--project',required=True)
    check=sub.add_parser('inspect').add_subparsers(dest='action',required=True)
    med=check.add_parser('media');med.add_argument('file');med.add_argument('--decode',action='store_true');med.add_argument('--out')
    bl=sub.add_parser('blender');bl.add_argument('arguments',nargs=argparse.REMAINDER)
    return p


def project_init(cfg,args):
    if not args.name or args.name in {'.','..'} or any(x in args.name for x in '/\\:'):
        raise ValueError('Use a single safe project folder name')
    root=Path(args.path).expanduser().absolute() if args.path else cfg.projects/args.name
    if root.exists():raise FileExistsError('Project exists; resume its existing state instead of creating it again')
    root.mkdir(parents=True)
    for n in ['inputs','assets','planning','runtime','delivery']: (root/n).mkdir()
    source=cfg.repository/'skills'/('game-production-workflows' if args.kind=='game' else 'video-production-workflows')/'assets'
    for item in source.iterdir():
        if item.is_file():shutil.copy2(item,root/'planning'/item.name)
    state={'schema_version':1,'project_id':args.name,'kind':args.kind,'root':str(root),'status':'not_started','requirements':[],
           'selected_assets':[],'pending_decisions':[],'evidence':[],'retained_caches':[],'next_action':'Read the project brief and relevant production Skill, then preserve user scope and start the applicable stage.'}
    write_new(root/'project.json',state)
    (root/'README.md').write_text(f'# {args.name}\n\n类型：{args.kind}。项目素材、脚本、日志、临时数据和交付物统一收纳于此。先完善planning中的简报，按对应总流程推进。\n\n不要将本项目特化画布覆盖通用库；需要时放原生Projects/{args.name}/<模型>/<功能>.json。\n','utf-8')
    return {'project':str(root),'state':'not_started','generated_content':False}


def cleanup_inventory(cfg,raw):
    root=Path(raw).expanduser().resolve()
    if not (root/'project.json').is_file():raise ValueError('A LightStory project.json is required to establish task ownership')
    rows=[]
    for folder in ['runtime','downloads']:
        p=root/folder
        if p.is_symlink():rows.append({'path':str(p),'skipped':'symlink'});continue
        size=sum(f.stat().st_size for f in p.rglob('*') if f.is_file() and not f.is_symlink()) if p.exists() else 0
        rows.append({'path':str(p),'bytes':size,'automatic_delete':False})
    disk=shutil.disk_usage(root)
    return {'project':str(root),'temporary_candidates':rows,'free_gib':disk.free/2**30,'rule':cfg.data.get('cleanup',{'check_hours':2,'growth_gib':30,'total_temporary_gib':60,'minimum_free_gib':60,'allow_necessary_growth':True}),
            'next':'Review exact ownership, running consumers and rework requirements, then remove only confirmed-unused paths with native literal-path commands. This command never deletes.'}


def execute(args,cfg):
    if args.command=='config':
        file=Path(args.out).expanduser().absolute() if args.out else cfg.repository/'config/local.json'
        write_new(file,read_json(cfg.repository/f'config/example.{args.template}.json'))
        return {'configuration':str(file),'next':'Edit paths/executables for this host; then run paths and doctor. No application or dependency was installed.'}
    if args.command=='paths':return cfg.summary()
    if args.command=='validate':return audit.validate(cfg)
    if args.command=='doctor':return audit.doctor(cfg,online=args.online,workflow=args.workflow)
    if args.command=='workflows':
        if args.action=='status':return workflows.status(cfg)
        if args.action=='list':return [x for x in workflows.catalog(cfg) if not args.model or x['model'].casefold()==args.model.casefold()]
        if args.action=='show':
            row=workflows.resolve(cfg,args.workflow);return {**row,'nodes':read_json(workflows.api(cfg,row))}
        return workflows.prepare(cfg,args.workflow,overrides=read_json(args.overrides) if args.overrides else None,prefix=args.prefix,out=args.out)
    if args.command=='models':
        items=models.selection(cfg,ids=args.ids,workflow=args.workflow,family=args.family)
        if args.action=='plan':return {'weights':items,'total_known_bytes':sum(x.get('size') or 0 for x in items),'downloaded':False}
        if args.action=='check':return models.inspect(cfg,items,args.hash)
        if not(args.ids or args.workflow or args.family):raise ValueError('Select --id, --workflow or --family before downloading; no implicit full-library download')
        return [models.acquire(cfg,x,acknowledge_license=args.acknowledge_license) for x in items]
    if args.command=='deps':
        return dependencies.registry(cfg) if args.action=='list' else dependencies.fetch(cfg,args.id,acknowledge_license=args.acknowledge_license)
    if args.command=='install':
        if args.action=='skills':return install.skills(cfg,agent=args.agent,target=args.target,upstream=args.with_upstream,apply=args.apply,copy=args.copy)
        if args.action=='workflows':return install.ui(cfg,target=args.target,apply=args.apply)
        return install.nodes(cfg,apply=args.apply)
    if args.command=='runtime':
        if args.action=='start':return runtime.start(cfg,args.profile,apply=args.apply,guard=not args.no_guard)
        if args.action=='stop':return runtime.stop(cfg,apply=args.apply,cancel=args.cancel)
        from .portal import serve
        serve(cfg,args.port or cfg.data.get('services',{}).get('preview_port',8192),args.with_history);return None
    if args.command=='project':return project_init(cfg,args)
    if args.command=='cleanup':return cleanup_inventory(cfg,args.project)
    if args.command=='inspect':
        from . import media
        result=media.inspect(cfg,args.file,decode=args.decode)
        if args.out:write_new(args.out,result)
        return result
    if args.command=='blender':
        helper=cfg.repository/'third_party/skills/blender-skills/blender-core/scripts/run_in_blender.py'
        env=os.environ.copy();exe=cfg.executable('blender')
        if exe:env['BLENDER_EXE']=exe
        child=subprocess.run([sys.executable,'-B','-X','utf8',str(helper),*args.arguments],env=env)
        if child.returncode:raise RuntimeError('Blender helper did not complete successfully')
        return None
    raise ValueError('Unknown command')


def main(argv=None):
    raw=list(sys.argv[1:] if argv is None else argv)
    command_index=2 if raw[:1]==['--config'] else 1 if raw and raw[0].startswith('--config=') else 0
    if len(raw)>command_index and raw[command_index]=='blender':
        args=parser().parse_args(raw[:command_index+1])
        args.arguments=raw[command_index+1:]
    else:args=parser().parse_args(raw)
    try:
        value=execute(args,Config.load(args.config))
        if value is not None:print(json.dumps(value,ensure_ascii=False,indent=2))
        if isinstance(value,dict) and (value.get('passed') is False or value.get('conflicts')):return 1
        return 0
    except (OSError,ValueError,RuntimeError,StopIteration) as error:
        print(json.dumps({'error':str(error)},ensure_ascii=False),file=sys.stderr);return 1
