"""The repository already includes synthetic documents under data/. This script validates them."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]/"data"
files=list(root.rglob("*.json"))
for f in files: json.loads(f.read_text())
print(f"Validated {len(files)} synthetic documents")
