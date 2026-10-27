#!/usr/bin/env python3
"""Serve only the published site/docs from the checkout, not caches or .git."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_ROOT_FILES = {"index.html", "README.md"}
ALLOWED_DIRS = {"docs", "research"}


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        resolved = Path(super().translate_path(path)).resolve()
        if resolved == ROOT:
            return str(ROOT)
        if not resolved.is_relative_to(ROOT):
            return str(ROOT / "__not_public__")
        parts = resolved.relative_to(ROOT).parts
        if (not parts or any(part.startswith(".") for part in parts)
                or not (len(parts) == 1 and parts[0] in ALLOWED_ROOT_FILES or parts[0] in ALLOWED_DIRS)):
            return str(ROOT / "__not_public__")
        return str(resolved)

    def list_directory(self, path: str):
        self.send_error(403, "Directory listing disabled")
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    handler = partial(Handler, directory=str(ROOT))
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Serving published files on {args.host}:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
