#!/usr/bin/env python3
"""Compare independent audit outputs while ignoring only their creation time."""
from pathlib import Path
import json
import sys

if len(sys.argv) != 3:
    raise SystemExit("Usage: compare_audit.py published.json reproduced.json")
a, b = (json.loads(Path(x).read_text()) for x in sys.argv[1:])
a.pop("generated_utc", None)
b.pop("generated_utc", None)
if a != b:
    raise SystemExit("Audit reproduction differs from the published snapshot")
print("Audit reproduction matches the published snapshot (except creation time).")
