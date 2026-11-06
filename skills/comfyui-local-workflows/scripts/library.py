"""Compatibility entry: the shared portable CLI owns catalog/configuration."""
from pathlib import Path
import sys
for parent in Path(__file__).resolve().parents:
    if (parent / "src/lightstory/cli.py").is_file():
        sys.path.insert(0, str(parent / "src")); break
from lightstory.cli import main
if __name__ == "__main__":
    raise SystemExit(main(["workflows", *sys.argv[1:]]))
