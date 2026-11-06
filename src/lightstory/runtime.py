"""Explicit service plans and owned-process lifecycle; no automatic activation."""
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.parse import urlsplit
from .config import read_json, write_new
from . import workflows


def backend_command_matches(command, source, port):
    normalized=[str(x).replace('\\','/') for x in command]
    return (str(source).replace('\\','/').casefold() in ' '.join(normalized).casefold()
            and any(x.rsplit('/',1)[-1].casefold()=='main.py' for x in normalized)
            and str(port) in normalized)


def start_plan(cfg, profile="Balanced", guard=True):
    if profile not in {"Default", "Balanced", "Conservative", "PixalStable"}: raise ValueError("Unknown startup profile")
    if not cfg.comfy or not (cfg.comfy / "main.py").is_file(): raise ValueError("Configure an installed ComfyUI root containing main.py")
    executable=cfg.executable('comfyui_python')
    if not executable or not Path(executable).is_file(): raise ValueError('Configure the existing ComfyUI Python interpreter')
    parsed=urlsplit(cfg.url);port=parsed.port or 8188
    args=[executable,'-u',str(cfg.comfy/'main.py'),'--listen',parsed.hostname,'--port',str(port),
          '--models-directory',str(cfg.models),'--input-directory',str(cfg.inputs),'--output-directory',str(cfg.outputs),
          '--temp-directory',str(cfg.runtime/'temp'),'--disable-auto-launch','--disable-partner-nodes','--reserve-vram','1.5']
    if profile in {'Balanced','Conservative','PixalStable'}:
        args[args.index('--reserve-vram')+1]='4'
        args += ['--use-split-cross-attention' if profile=='PixalStable' else '--use-pytorch-cross-attention','--disable-async-offload','--disable-pinned-memory','--disable-cuda-malloc','--cache-none']
    if profile=='Balanced':args += ['--enable-dynamic-vram','--fast-disk']
    if profile=='Conservative':args += ['--disable-dynamic-vram']
    return {'profile':profile,'port':port,'command':args,'cwd':str(cfg.comfy),'guard':guard and sys.platform=='win32','runtime':str(cfg.runtime),'applied':False}


def start(cfg, profile='Balanced', *, apply=False, guard=True):
    plan=start_plan(cfg,profile,guard)
    if not apply:return plan
    try:
        workflows.http(cfg,'/system_stats')
        return {'reused':True,'url':cfg.url,'profile_changed':False}
    except OSError:pass
    if plan['guard']:
        try:import psutil
        except ImportError as error:raise RuntimeError('Memory guard requires system-Python psutil; install the windows extra first') from error
    # Validate this version's flags before starting; a missing flag is a setup error, not permission to downgrade the profile.
    help_=subprocess.run([plan['command'][0],str(cfg.comfy/'main.py'),'--help'],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=30)
    if help_.returncode:raise RuntimeError('ComfyUI --help failed; inspect its environment first')
    unsupported=[x for x in plan['command'] if x.startswith('--') and x not in help_.stdout]
    if unsupported:raise ValueError('Configured ComfyUI version lacks required flags: '+', '.join(unsupported))
    env=os.environ.copy();env.update(PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1',LIGHTSTORY_ROOT=str(cfg.repository),LIGHTSTORY_CONFIG=str(cfg.file))
    env['PYTHONPATH']=str(cfg.repository/'src')+os.pathsep+env.get('PYTHONPATH','')
    dirs={'TEMP':'temp/system','TMP':'temp/system','TMPDIR':'temp/system','TORCHINDUCTOR_CACHE_DIR':'temp/torchinductor','TRITON_CACHE_DIR':'temp/triton','CUDA_CACHE_PATH':'temp/cuda','COMFYUI_H3_CACHE_DIR':'cache/h3','MPLCONFIGDIR':'matplotlib','YOLO_CONFIG_DIR':'yolo'}
    for key,tail in dirs.items():
        path=cfg.runtime/tail;path.mkdir(parents=True,exist_ok=True);env[key]=str(path)
    cache=cfg.path('model_cache_root')
    if cache:env.update(HF_HOME=str(cache/'huggingface'),TORCH_HOME=str(cache/'torch'))
    env['OPENBLAS_NUM_THREADS']='1'
    logs=cfg.runtime/'logs';logs.mkdir(parents=True,exist_ok=True)
    timestamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out=logs/(timestamp+'.stdout.log');err=logs/(timestamp+'.stderr.log')
    kwargs={'creationflags':subprocess.CREATE_NO_WINDOW} if sys.platform=='win32' else {'start_new_session':True}
    with out.open('ab') as stdout,err.open('ab') as stderr:
        worker=subprocess.Popen(plan['command'],cwd=cfg.comfy,env=env,stdout=stdout,stderr=stderr,**kwargs)
    record={'owner':'lightstory start','pid':worker.pid,'source':str(cfg.comfy),'port':plan['port'],'profile':profile,'arguments':plan['command'][1:],'started_at':time.time(),'stdout':str(out),'stderr':str(err)}
    try:
        import psutil
        record['create_time']=psutil.Process(worker.pid).create_time()
    except (ImportError,OSError):pass
    (cfg.runtime/'process.json').write_text(json.dumps(record,indent=2)+'\n','utf-8')
    if plan['guard']:
        with (logs/(timestamp+'.guard.log')).open('ab') as log:
            helper=subprocess.Popen([sys.executable,'-B','-X','utf8',str(cfg.repository/'adapters/comfyui/runtime/memory_guard.py'),'--port',str(plan['port'])],env=env,stdout=log,stderr=log,**kwargs)
        record['guard_pid']=helper.pid
        (cfg.runtime/'process.json').write_text(json.dumps(record,indent=2)+'\n','utf-8')
    return {'applied':True,'process':record,'ready':False,'next':'Wait for /system_stats and check startup logs; process creation alone is not startup success.'}


def stop(cfg, *, apply=False, cancel=False):
    record=read_json(cfg.runtime/'process.json',{})
    if not record:return {'stopped':False,'reason':'No owned process record; use the application that launched the service'}
    if record.get('owner')!='lightstory start' or record.get('source')!=str(cfg.comfy):raise ValueError('Process record is not owned by this configuration')
    if not apply:return {'applied':False,'record':record,'cancel_running':cancel}
    try:import psutil
    except ImportError as e:raise RuntimeError('Install psutil to verify owned PID identity before stopping') from e
    try:root=psutil.Process(record['pid'])
    except psutil.NoSuchProcess:return {'stopped':False,'already_exited':True}
    if record.get('create_time') and abs(root.create_time()-record['create_time'])>0.05:raise ValueError('Recorded PID has been reused')
    if not backend_command_matches(root.cmdline(),cfg.comfy,record['port']):raise ValueError('Process command does not match configured ComfyUI')
    try:
        q=workflows.http(cfg,'/queue');running=q.get('queue_running',[]);pending=q.get('queue_pending',[])
        if (running or pending) and not cancel:raise ValueError('Backend has work; preserve it or explicitly pass --cancel')
        if pending:workflows.http(cfg,'/queue',{'delete':[x[1] for x in pending]})
        if running:workflows.http(cfg,'/interrupt',{})
    except OSError:pass
    processes=root.children(recursive=True)+[root]
    guard_pid=record.get('guard_pid')
    if guard_pid:
        try:
            g=psutil.Process(guard_pid)
            if str(cfg.repository/'adapters/comfyui/runtime/memory_guard.py') in ' '.join(g.cmdline()):processes.append(g)
        except psutil.NoSuchProcess:pass
    stopped=[]
    for p in processes:
        if not p.is_running():continue
        if sys.platform=='win32':
            subprocess.run(['powershell','-NoProfile','-Command',f'Stop-Process -Id {int(p.pid)} -ErrorAction Stop'],check=True,capture_output=True)
        else:p.terminate()
        stopped.append(p.pid)
    return {'stopped':True,'pids':stopped,'record_retained':True}
