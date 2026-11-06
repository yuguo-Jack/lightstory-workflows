"""Maintainer export into a new, reviewable directory; never modifies native graphs."""
from pathlib import Path
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from lightstory.config import Config
from lightstory.exporter import export
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config');p.add_argument('--source-catalog',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    print(json.dumps(export(Config.load(a.config),a.source_catalog,a.out),ensure_ascii=False,indent=2))
