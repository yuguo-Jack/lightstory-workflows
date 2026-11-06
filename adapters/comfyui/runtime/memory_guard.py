"""Reclaim owned Pixal residency early; interrupt if desktop reserves are low."""
import argparse
import ctypes
import json
import msvcrt
import os
from pathlib import Path
import time
import urllib.request

from owned_working_set import trim_owned_backend

from lightstory.config import Config
_cfg = Config.load()
ROOT = _cfg.state_root
RUNTIME=ROOT/'runtime'
RESOURCES=_cfg.data.get('resources',{})
RESERVE_COMMIT=float(RESOURCES.get('reserve_commit_gib',6))
RESERVE_RAM=float(RESOURCES.get('reserve_ram_gib',2.5))
HEAVY_MIN_COMMIT=float(RESOURCES.get('heavy_minimum_commit_gib',63))


class MemoryStatus(ctypes.Structure):
    _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[(name,ctypes.c_ulonglong) for name in ['total_phys','avail_phys','total_pagefile','avail_pagefile','total_virtual','avail_virtual','avail_extended']]


def memory():
    state=MemoryStatus();state.length=ctypes.sizeof(state)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state)):
        raise ctypes.WinError()
    return {'commit_limit_GiB':state.total_pagefile/2**30,'commit_headroom_GiB':state.avail_pagefile/2**30,'available_RAM_GiB':state.avail_phys/2**30}


def require_headroom(minimum_commit_GiB=8,*,needs_expanded_pagefile=False):
    state=memory()
    if needs_expanded_pagefile and state['commit_limit_GiB']<HEAVY_MIN_COMMIT:
        raise RuntimeError('当前提交上限低于配置的重任务最低值；检查分页文件和重启状态。当前提交上限'+str(round(state['commit_limit_GiB'],2))+'GiB')
    if state['commit_headroom_GiB']<minimum_commit_GiB or state['available_RAM_GiB']<3:
        raise RuntimeError('Memory preflight refused this test to preserve desktop headroom: '+json.dumps(state))
    return state


def call(url,route,data=None):
    request=urllib.request.Request(url+route,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=3) as response:
        data=response.read()
    return json.loads(data) if data else {}


def heavy(prompt):
    for node in prompt.values():
        kind=node.get('class_type','')
        if kind=='MiniMaxH3Director' or kind.startswith('Ming') or 'MiniMaxMusic' in kind:
            return True
        if kind=='TextEncodeQwenImage21' and sum(key.startswith('images.image_') for key in node.get('inputs',{}))>=5:
            return True
    return False


def pixal(prompt):
    return any(node.get('class_type', '').startswith('Pixal3D') for node in prompt.values())


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8188);args=parser.parse_args()
    RUNTIME.mkdir(parents=True,exist_ok=True)
    lock=(RUNTIME/'memory_guard.lock').open('a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
    try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    except OSError:print('A memory guard already owns this runtime',flush=True);return
    url=_cfg.url;last_queue=0;last_write=0;last_id=None;last_trim=0
    previous={}
    try:previous=json.loads((RUNTIME/'memory_guard.json').read_text(encoding='utf-8-sig'))
    except (OSError,ValueError):pass
    state={'pid':os.getpid(),'port':args.port,'owner':'lightstory memory_guard','reserve_commit_GiB':RESERVE_COMMIT,'reserve_RAM_GiB':RESERVE_RAM,'heavy_minimum_commit_GiB':HEAVY_MIN_COMMIT,'started_at':time.time(),'interrupts':previous.get('interrupts',0),'session_interrupts':0,'residency_reclaim_enabled':True,'residency_reclaim_RAM_trigger_GiB':8,'residency_trims':0}
    if previous.get('last_interrupt'):state['last_interrupt']=previous['last_interrupt']
    while True:
        now=time.time();sample=memory();state.update(sample,at=now)
        pressure=sample['commit_headroom_GiB']<RESERVE_COMMIT or sample['available_RAM_GiB']<RESERVE_RAM
        if pressure or now-last_queue>2:
            last_queue=now
            try:
                queue=call(url,'/queue');state['backend_online']=True
                running=queue.get('queue_running',[])
                if running:
                    identifier=running[0][1];prompt=running[0][2]
                    pending_expansion=sample['commit_limit_GiB']<HEAVY_MIN_COMMIT and heavy(prompt)
                    # Reclaim before reaching the original hard reserve. This
                    # only applies to Pixal graphs in our verified owned PID.
                    # Other models keep their existing protection behavior.
                    if (not pressure and pixal(prompt) and sample['available_RAM_GiB']<8
                            and sample['commit_headroom_GiB']>=10 and now-last_trim>=4):
                        last_trim=now
                        try:
                            event=trim_owned_backend(args.port,identifier)
                            event.update(before_available_RAM_GiB=sample['available_RAM_GiB'],commit_headroom_GiB=sample['commit_headroom_GiB'])
                            with (RUNTIME/'memory_guard.events.jsonl').open('a',encoding='utf-8') as file:file.write(json.dumps(event,ensure_ascii=False)+'\n')
                            state['last_residency_trim']=event;state['residency_trims']+=1
                            print(json.dumps(event,ensure_ascii=False),flush=True)
                        except Exception as error:
                            state['last_residency_error']=str(error)
                    if (pressure or pending_expansion) and identifier!=last_id:
                        call(url,'/interrupt',{})
                        event={'at':now,'prompt_id':identifier,'reason':'pagefile_resize_requires_restart' if pending_expansion else 'desktop_memory_reserve',**sample}
                        with (RUNTIME/'memory_guard.events.jsonl').open('a',encoding='utf-8') as file:file.write(json.dumps(event,ensure_ascii=False)+'\n')
                        state['last_interrupt']=event;state['interrupts']+=1;state['session_interrupts']+=1;last_id=identifier
                        print(json.dumps(event,ensure_ascii=False),flush=True)
                else:last_id=None
            except Exception as error:
                state['backend_online']=False;state['last_connection_error']=type(error).__name__
        if now-last_write>3:
            last_write=now
            temporary=RUNTIME/'memory_guard.json.tmp';temporary.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8');temporary.replace(RUNTIME/'memory_guard.json')
        time.sleep(0.5)


if __name__=='__main__':main()
