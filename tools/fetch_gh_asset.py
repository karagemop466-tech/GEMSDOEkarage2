"""Fetch a file from a GitHub repo via the API (base64 inline content).

Used because raw.githubusercontent.com and dropbox are blocked in this sandbox,
while api.github.com is reachable and returns file content inline for files < 1 MB.
"""
import base64
import json
import sys
import urllib.request

API = "https://api.github.com/repos/buffedlizard55-lab/GEMSDOE36/contents/"


def fetch(path: str, out: str) -> None:
    url = API + path
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "GEMSDOEkarage2-agent"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    if data.get("type") != "file":
        raise SystemExit(f"not a file: {path} (type={data.get('type')})")
    encoding = data.get("encoding")
    size = data.get("size")
    raw = base64.b64decode(data["content"])
    if len(raw) != size:
        raise SystemExit(f"size mismatch for {path}: {len(raw)} != {size}")
    with open(out, "wb") as f:
        f.write(raw)
    print(f"OK {path} -> {out} ({len(raw)} bytes, sha={data['sha'][:12]})")


if __name__ == "__main__":
    # usage: python fetch_gh_asset.py <repo-path> <out-file>
    fetch(sys.argv[1], sys.argv[2])
