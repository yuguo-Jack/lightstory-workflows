"""Windows residency cleanup restricted to this workspace's owned ComfyUI.

Uses the documented K32EmptyWorkingSet hint. Allocations and tensor values are
preserved. No persistent working-set limit or system paging policy is changed.
"""
import ctypes
import json
from pathlib import Path
import time
import urllib.request

import psutil

from lightstory.config import Config
from lightstory.runtime import backend_command_matches
_cfg = Config.load()
ROOT = _cfg.state_root
COMFY = _cfg.comfy


def trim_owned_backend(port, prompt_id):
    record = json.loads((ROOT / "runtime/process.json").read_text("utf-8-sig"))
    if record.get("owner") != "lightstory start" or record.get("source") != str(COMFY) or record.get("port") != port:
        raise RuntimeError("Process record does not identify our controlled ComfyUI")
    listeners = [conn for conn in psutil.net_connections(kind="tcp")
                 if conn.status == "LISTEN" and conn.laddr.port == port and conn.laddr.ip in ("127.0.0.1", "::1")]
    if len(listeners) != 1 or listeners[0].pid is None:
        raise RuntimeError("Controlled localhost listener cannot be identified uniquely")
    process = psutil.Process(listeners[0].pid)
    command = process.cmdline()
    if not backend_command_matches(command, COMFY, port):
        raise RuntimeError("Listener process is not this ComfyUI installation")
    owner = psutil.Process(record["pid"])
    if process.pid != owner.pid and owner.pid not in [parent.pid for parent in process.parents()]:
        raise RuntimeError("Listener is not the recorded backend or its child")
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/queue", timeout=3) as response:
        queue = json.load(response)
    if not any(job[1] == prompt_id for job in queue.get("queue_running", [])):
        raise RuntimeError("The expected generation is not currently running")
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_bool, ctypes.c_ulong]
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.K32EmptyWorkingSet.argtypes = [ctypes.c_void_p]
    kernel.K32EmptyWorkingSet.restype = ctypes.c_bool
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel.CloseHandle.restype = ctypes.c_bool
    handle = kernel.OpenProcess(0x0400 | 0x0100, False, process.pid)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        before = process.memory_info().rss
        if not kernel.K32EmptyWorkingSet(handle):
            raise ctypes.WinError(ctypes.get_last_error())
        return {"type": "working_set_trim", "at": time.time(), "backend_pid": process.pid,
                "prompt_id": prompt_id, "before_working_set_GiB": before / 2**30,
                "after_working_set_GiB": process.memory_info().rss / 2**30,
                "success": True, "method": "Windows K32EmptyWorkingSet; allocations and tensor values preserved"}
    finally:
        kernel.CloseHandle(handle)
