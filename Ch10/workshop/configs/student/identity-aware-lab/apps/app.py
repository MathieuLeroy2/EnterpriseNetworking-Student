"""Small header-inspection app for the chapter 10 forward-auth lab.

The app deliberately has no local login. It displays selected headers that should
only reach it through the trusted reverse-proxy path. It is a teaching aid, not a
production remote-user implementation.
"""

from __future__ import annotations

import html
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


APP_TITLE = os.environ.get("APP_TITLE", "BluePeak application")
APP_AUDIENCE = os.environ.get("APP_AUDIENCE", "Onbekend")
APP_SENSITIVITY = os.environ.get("APP_SENSITIVITY", "Onbekend")

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


def render_page(headers: BaseHTTPRequestHandler.headers) -> bytes:
    rows = []
    for name in SHOWN_HEADERS:
        value = headers.get(name, "niet aanwezig")
        rows.append(f"<tr><th>{escape(name)}</th><td>{escape(value)}</td></tr>")

    identity = headers.get("X-Authentik-Username")
    if identity:
        identity_message = (
            f'<div class="ok">Forward auth gaf toegang voor '
            f'<strong>{escape(identity)}</strong>.</div>'
        )
    else:
        identity_message = (
            '<div class="public">Geen Authentik-identiteit ontvangen. Dit is alleen '
            'verwacht voor de publieke route.</div>'
        )

    document = f"""<!doctype html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(APP_TITLE)}</title>
  <style>
    :root {{ font-family: Inter, "Segoe UI", Arial, sans-serif; color: #18222d; }}
    body {{ margin: 0; background: #f3f5f7; }}
    header {{ background: #123c4a; color: white; padding: 1rem 1.5rem;
              border-bottom: 4px solid #e3b341; }}
    main {{ width: min(960px, calc(100% - 2rem)); margin: 2rem auto; }}
    section {{ background: white; border: 1px solid #ccd4da; border-radius: 6px;
               padding: 1.25rem; margin-bottom: 1rem; }}
    h1 {{ margin-top: 0; }}
    .ok, .public {{ padding: .8rem 1rem; border-left: 5px solid #2a7f62;
                    background: #eef8f3; }}
    .public {{ border-left-color: #126e82; background: #edf7fa; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border: 1px solid #d6dde2; padding: .6rem; text-align: left;
              overflow-wrap: anywhere; }}
    th {{ width: 35%; background: #f5f7f8; }}
    code {{ background: #edf0f2; padding: .1rem .25rem; }}
  </style>
</head>
<body>
  <header><strong>BluePeak Services | Identity-aware lab</strong></header>
  <main>
    <section>
      <h1>{escape(APP_TITLE)}</h1>
      <p><strong>Doelgroep:</strong> {escape(APP_AUDIENCE)}<br>
         <strong>Classificatie:</strong> {escape(APP_SENSITIVITY)}</p>
      {identity_message}
    </section>
    <section>
      <h2>Ontvangen proxy- en identity-headers</h2>
      <table><tbody>{''.join(rows)}</tbody></table>
    </section>
    <section>
      <h2>Vertrouwensgrens</h2>
      <p>Deze demo toont headers om het pad zichtbaar te maken. Een productieapp mag
      <code>X-Authentik-*</code> alleen vertrouwen wanneer de backend niet rechtstreeks
      bereikbaar is en alleen een vertrouwde proxy die headers kan zetten.</p>
    </section>
  </main>
</body>
</html>"""
    return document.encode("utf-8")


class AppHandler(BaseHTTPRequestHandler):
    server_version = "BluePeakHeaderLab/1.0"

    def log_message(self, format_string: str, *args: object) -> None:
        username = self.headers.get("X-Authentik-Username", "anonymous")
        print(
            f"{self.client_address[0]} user={username} "
            f"{format_string % args}",
            flush=True,
        )

    def do_HEAD(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
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

        body = render_page(self.headers)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print(f"{APP_TITLE} listening on 0.0.0.0:8080", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8080), AppHandler).serve_forever()

