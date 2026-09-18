"""Check local Markdown links and parse illustrative JSON; not conformance tests."""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
errors = []
excluded = {".git", ".venv", "node_modules", "__pycache__"}
for path in root.rglob("*.json"):
    if not excluded.intersection(path.relative_to(root).parts):
        try:
            json.loads(path.read_text())
        except ValueError as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
for path in root.rglob("*.md"):
    if excluded.intersection(path.relative_to(root).parts):
        continue
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
        if "://" in target or target.startswith(("#", "mailto:")):
            continue
        local = target.split("#", 1)[0]
        if local and not (path.parent / local).exists():
            errors.append(f"{path.relative_to(root)}: missing {local}")
if errors:
    raise SystemExit("\n".join(errors))
print("Local Markdown links resolve; illustrative JSON parses.")
