"""Author a new flat UI graph from API plus explicit/live object_info; never overwrite."""
from pathlib import Path
import argparse
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'adapters/comfyui')]
from lightstory.config import Config,read_json,write_new
from lightstory.workflows import http
from graph_tools import api_to_ui

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--api',required=True);p.add_argument('--object-info');p.add_argument('--out',required=True);p.add_argument('--config');a=p.parse_args()
    info=read_json(a.object_info) if a.object_info else http(Config.load(a.config),'/object_info')
    write_new(a.out,api_to_ui(read_json(a.api),info=info))
    print(json.dumps({'workflow':str(Path(a.out).resolve()),'submitted':False,'next':'Read back graphToPrompt in the current frontend; dynamic/custom widgets may need manual layout or node-specific adaptation.'}))
