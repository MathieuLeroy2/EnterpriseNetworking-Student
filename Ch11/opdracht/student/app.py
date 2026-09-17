"""Header-inspection app for the PixelPeak admin route."""

from __future__ import annotations

import html
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


APP_TITLE = os.environ.get("APP_TITLE", "PixelPeak admin")
APP_AUDIENCE = os.environ.get("APP_AUDIENCE", "IT-beheerders")
APP_SENSITIVITY = os.environ.get("APP_SENSITIVITY", "Intern")
SHOWN_HEADERS = (
    "X-Authentik-Username",
    "X-Authentik-Groups",
    "X-Authentik-Email",
    "X-Authentik-Name",
    "X-Authentik-Uid",
    "X-Authentik-Meta-App",
    "X-Authentik-Meta-Provider",
    "X-Forwarded-Host",
    "X-Forwarded-Proto",
)


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def page(headers: object) -> bytes:
    rows = []
    for name in SHOWN_HEADERS:
        value = headers.get(name, "niet aanwezig")
        rows.append(f"<tr><th>{escape(name)}</th><td>{escape(value)}</td></tr>")

    username = headers.get("X-Authentik-Username")
    status = (
        f"Forward auth gaf toegang voor <strong>{escape(username)}</strong>."
        if username
        else "Geen Authentik-identiteit ontvangen; alleen verwacht na forward auth."
    )

    return f"""<!doctype html><html lang="nl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(APP_TITLE)}</title><style>
body{{font-family:Segoe UI,Arial,sans-serif;margin:0;background:#f3f5f7;color:#18222d}}
header{{background:#123c4a;color:#fff;padding:1rem 1.5rem;border-bottom:4px solid #e3b341}}
main{{width:min(960px,calc(100% - 2rem));margin:2rem auto}}section{{background:#fff;
border:1px solid #ccd4da;border-radius:6px;padding:1.25rem;margin-bottom:1rem}}
table{{width:100%;border-collapse:collapse}}th,td{{border:1px solid #d6dde2;padding:.6rem;
text-align:left;overflow-wrap:anywhere}}th{{width:35%;background:#f5f7f8}}
.status{{padding:.8rem 1rem;border-left:5px solid #2a7f62;background:#eef8f3}}
</style></head><body><header><strong>PixelPeak Services | Identity-aware lab</strong></header>
<main><section><h1>{escape(APP_TITLE)}</h1><p><strong>Doelgroep:</strong>
{escape(APP_AUDIENCE)}<br><strong>Classificatie:</strong> {escape(APP_SENSITIVITY)}</p>
<div class="status">{status}</div></section><section><h2>Ontvangen headers</h2>
<table><tbody>{''.join(rows)}</tbody></table></section><section><h2>Vertrouwensgrens</h2>
<p>Vertrouw deze headers alleen wanneer clients de backend niet rechtstreeks kunnen
bereiken en alleen een vertrouwde proxy de headers kan zetten.</p></section></main></body></html>""".encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "PixelPeakHeaderLab/1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        user = self.headers.get("X-Authentik-Username", "anonymous")
        print(f"{self.client_address[0]} user={user} {fmt % args}", flush=True)

    def do_HEAD(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/healthz":
            body = b"ok\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path != "/":
            self.send_error(404)
            return

        body = page(self.headers)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print(f"{APP_TITLE} listening on 0.0.0.0:8080", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()