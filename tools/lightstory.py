#!/usr/bin/env python3
"""Run from a source checkout without installing a Python package."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from lightstory.cli import main
if __name__ == "__main__":
    raise SystemExit(main())
