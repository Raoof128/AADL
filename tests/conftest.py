import sys
from pathlib import Path

# Ensure src/ is importable during tests without installation
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

src_path = root / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

extra_paths = [root / "attacks", root / "defence", root / "detection"]
for path in extra_paths:
    if path.exists():
        sys.path.insert(0, str(path))
