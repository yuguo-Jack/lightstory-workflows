"""Regenerate the standalone overview from the canonical workflow catalog."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from lightstory.config import Config
from lightstory.portal import page

if __name__ == '__main__':
    cfg = Config(ROOT, ROOT / 'config/local.json', {})
    target = ROOT / 'docs/overview.html'
    target.write_text(page(cfg), encoding='utf-8', newline='\n')
    print(target.relative_to(ROOT).as_posix())
