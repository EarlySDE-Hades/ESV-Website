"""Preview the site locally the way Vercel serves it: clean URLs (/about serves about.html,
/about.html redirects to /about) and 404.html for anything missing.

    python tools/serve.py          # http://127.0.0.1:5173
    python tools/serve.py 8080
"""
import http.server
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _route(self):
        parts = urlsplit(self.path)
        path = parts.path
        if path.endswith(".html"):   # same as Vercel: the .html address moves to the clean one
            clean = "/" if path == "/index.html" else path[:-5]
            self.send_response(308)
            self.send_header("Location", clean + (f"?{parts.query}" if parts.query else ""))
            self.end_headers()
            return False
        local = ROOT / path.lstrip("/")
        if path != "/" and not local.exists() and local.with_suffix(".html").is_file():
            self.path = path + ".html" + (f"?{parts.query}" if parts.query else "")
        elif path != "/" and not local.exists():
            body = (ROOT / "404.html").read_bytes()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if self.command == "GET":
                self.wfile.write(body)
            return False
        return True

    def do_GET(self):
        if self._route():
            super().do_GET()

    def do_HEAD(self):
        if self._route():
            super().do_HEAD()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5173
    print(f"Serving on http://127.0.0.1:{port}")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
