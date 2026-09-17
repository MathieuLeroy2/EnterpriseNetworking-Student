"""Small dependency-free OIDC client for the chapter 9 identity lab.

This client deliberately exposes the shape of the authorization code flow. It is
not a production OIDC implementation: it does not validate JWT signatures and it
uses HTTP on localhost. Identity displayed after login comes from the UserInfo
endpoint, not from an unverified token payload.
"""

from __future__ import annotations

import html
import json
import os
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


CLIENT_ID = os.environ.get("OIDC_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("OIDC_CLIENT_SECRET", "")
AUTHORIZATION_URL = os.environ.get("OIDC_AUTHORIZATION_URL", "")
TOKEN_URL = os.environ.get("OIDC_TOKEN_URL", "")
USERINFO_URL = os.environ.get("OIDC_USERINFO_URL", "")
REDIRECT_URI = os.environ.get("OIDC_REDIRECT_URI", "http://localhost:8089/callback")
SCOPES = os.environ.get("OIDC_SCOPES", "openid profile email")

PENDING_LOGINS: dict[str, dict[str, str | float]] = {}
SESSIONS: dict[str, dict[str, object]] = {}


def configured() -> bool:
    markers = ("", "CHANGE_ME_AFTER_PROVIDER_CREATION")
    return CLIENT_ID not in markers and CLIENT_SECRET not in markers


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_claims(claims: dict[str, object]) -> str:
    if not claims:
        return "<p class=\"muted\">Geen claims ontvangen.</p>"

    rows = []
    for key in sorted(claims):
        value = claims[key]
        if isinstance(value, (dict, list)):
            shown = json.dumps(value, ensure_ascii=True, indent=2)
        else:
            shown = str(value)
        rows.append(
            f"<tr><th>{escape(key)}</th><td><pre>{escape(shown)}</pre></td></tr>"
        )
    return "<table><tbody>" + "".join(rows) + "</tbody></table>"


def page(title: str, body: str) -> bytes:
    document = f"""<!doctype html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} - BluePeak OIDC Lab</title>
  <style>
    :root {{
      color-scheme: light;
      font-family: Inter, "Segoe UI", Arial, sans-serif;
      background: #f3f5f7;
      color: #18222d;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; }}
    header {{
      background: #123c4a;
      color: white;
      padding: 1rem 1.5rem;
      border-bottom: 4px solid #e3b341;
    }}
    header strong {{ font-size: 1.1rem; }}
    main {{ width: min(960px, calc(100% - 2rem)); margin: 2rem auto; }}
    section {{
      background: white;
      border: 1px solid #ccd4da;
      border-radius: 6px;
      padding: 1.25rem;
      margin-bottom: 1rem;
    }}
    h1 {{ font-size: 1.65rem; margin: 0 0 0.75rem; }}
    h2 {{ font-size: 1.1rem; margin: 0 0 0.75rem; }}
    p {{ line-height: 1.55; }}
    a.button {{
      display: inline-block;
      background: #126e82;
      color: white;
      padding: 0.65rem 0.9rem;
      text-decoration: none;
      border-radius: 4px;
      font-weight: 650;
      margin-right: 0.5rem;
    }}
    a.secondary {{ background: #4c5963; }}
    .status {{
      border-left: 5px solid #2a7f62;
      background: #eef8f3;
      padding: 0.8rem 1rem;
    }}
    .warning {{
      border-left: 5px solid #b56a19;
      background: #fff7e8;
      padding: 0.8rem 1rem;
    }}
    .muted {{ color: #52616b; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{
      border: 1px solid #d6dde2;
      padding: 0.6rem;
      text-align: left;
      vertical-align: top;
    }}
    th {{ width: 28%; background: #f5f7f8; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; margin: 0; }}
    code {{ background: #edf0f2; padding: 0.1rem 0.25rem; }}
  </style>
</head>
<body>
  <header><strong>BluePeak Services | OIDC Lab Client</strong></header>
  <main>{body}</main>
</body>
</html>"""
    return document.encode("utf-8")


class OIDCHandler(BaseHTTPRequestHandler):
    server_version = "BluePeakOIDCLab/1.0"

    def log_message(self, format_string: str, *args: object) -> None:
        print(
            f"{self.client_address[0]} - "
            f"{format_string % args}",
            flush=True,
        )

    def send_html(self, status: int, title: str, body: str) -> None:
        content = page(title, body)
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'")
        self.end_headers()
        self.wfile.write(content)

    def redirect(self, location: str, cookie: str | None = None) -> None:
        self.send_response(302)
        self.send_header("Location", location)
        self.send_header("Cache-Control", "no-store")
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()

    def current_session(self) -> tuple[str | None, dict[str, object] | None]:
        raw_cookie = self.headers.get("Cookie", "")
        jar = cookies.SimpleCookie()
        try:
            jar.load(raw_cookie)
        except cookies.CookieError:
            return None, None
        morsel = jar.get("lab_session")
        if not morsel:
            return None, None
        session_id = morsel.value
        return session_id, SESSIONS.get(session_id)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        routes = {
            "/": self.home,
            "/login": self.login,
            "/callback": self.callback,
            "/logout": self.logout,
            "/healthz": self.health,
        }
        handler = routes.get(parsed.path)
        if not handler:
            self.send_html(404, "Niet gevonden", "<section><h1>404</h1></section>")
            return
        handler(parsed)

    def home(self, _parsed: urllib.parse.ParseResult) -> None:
        _session_id, session = self.current_session()
        if not configured():
            self.send_html(
                200,
                "Configuratie nodig",
                """
<section>
  <h1>OIDC-client nog niet gekoppeld</h1>
  <div class="warning">
    Vul <code>OIDC_CLIENT_ID</code> en <code>OIDC_CLIENT_SECRET</code> in
    <code>.env</code> in en voer <code>docker compose up -d</code> opnieuw uit.
  </div>
</section>
""",
            )
            return

        if not session:
            self.send_html(
                200,
                "Aanmelden",
                """
<section>
  <h1>Medewerkersportaal</h1>
  <p>Deze lokale applicatie bewaart geen gebruikerswachtwoorden. Aanmelden wordt
  gedelegeerd aan Authentik via OpenID Connect.</p>
  <a class="button" href="/login">Aanmelden via Authentik</a>
</section>
<section>
  <h2>Onderzoeksvraag</h2>
  <p class="muted">Welke partij authenticeert de gebruiker, welke identity-informatie
  ontvangt de applicatie en waar wordt toegang geweigerd?</p>
</section>
""",
            )
            return

        claims = session.get("userinfo")
        if not isinstance(claims, dict):
            claims = {}
        username = claims.get("preferred_username") or claims.get("name") or claims.get("sub")
        self.send_html(
            200,
            "Aangemeld",
            f"""
<section>
  <h1>Welkom, {escape(username or "onbekende gebruiker")}</h1>
  <div class="status">Authenticatie via Authentik is geslaagd en de OIDC-client heeft
  een lokale applicatiesessie gemaakt.</div>
  <p>
    <a class="button" href="/">Pagina vernieuwen</a>
    <a class="button secondary" href="/logout">Alleen lokaal uitloggen</a>
  </p>
</section>
<section>
  <h2>UserInfo-claims</h2>
  {render_claims(claims)}
</section>
<section>
  <h2>Tokenhygiëne</h2>
  <p class="muted">De labclient ontving tokens, maar toont ze niet. Neem volledige
  tokens nooit op in screenshots, logs of verslagen.</p>
</section>
""",
        )

    def login(self, _parsed: urllib.parse.ParseResult) -> None:
        if not configured():
            self.redirect("/")
            return
        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)
        PENDING_LOGINS[state] = {"nonce": nonce, "created": time.time()}
        query = urllib.parse.urlencode(
            {
                "client_id": CLIENT_ID,
                "response_type": "code",
                "redirect_uri": REDIRECT_URI,
                "scope": SCOPES,
                "state": state,
                "nonce": nonce,
            }
        )
        self.redirect(f"{AUTHORIZATION_URL}?{query}")

    def callback(self, parsed: urllib.parse.ParseResult) -> None:
        query = urllib.parse.parse_qs(parsed.query)
        if "error" in query:
            description = query.get("error_description", query["error"])[0]
            self.send_html(
                403,
                "Toegang geweigerd",
                f"<section><h1>OIDC-aanvraag geweigerd</h1>"
                f"<div class=\"warning\">{escape(description)}</div></section>",
            )
            return

        code = query.get("code", [""])[0]
        state = query.get("state", [""])[0]
        pending = PENDING_LOGINS.pop(state, None)
        if not code or not pending:
            self.send_html(
                400,
                "Ongeldige callback",
                "<section><h1>Ongeldige callback</h1>"
                "<div class=\"warning\">Code ontbreekt of state-controle faalde.</div>"
                "</section>",
            )
            return
        if time.time() - float(pending["created"]) > 300:
            self.send_html(
                400,
                "Callback vervallen",
                "<section><h1>Loginpoging vervallen</h1></section>",
            )
            return

        try:
            token_data = self.exchange_code(code)
            access_token = token_data.get("access_token")
            if not isinstance(access_token, str) or not access_token:
                raise ValueError("Token endpoint gaf geen access token terug.")
            userinfo = self.fetch_userinfo(access_token)
        except (urllib.error.URLError, ValueError, json.JSONDecodeError) as error:
            self.send_html(
                502,
                "Tokenuitwisseling mislukt",
                f"<section><h1>Tokenuitwisseling mislukt</h1>"
                f"<div class=\"warning\">{escape(error)}</div>"
                "<p>Controleer client ID, client secret, redirect URI en containerlogs.</p>"
                "</section>",
            )
            return

        session_id = secrets.token_urlsafe(32)
        SESSIONS[session_id] = {
            "userinfo": userinfo,
            "created": time.time(),
        }
        cookie = (
            f"lab_session={session_id}; Path=/; HttpOnly; SameSite=Lax; Max-Age=3600"
        )
        self.redirect("/", cookie)

    def exchange_code(self, code: str) -> dict[str, object]:
        body = urllib.parse.urlencode(
            {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            }
        ).encode("ascii")
        request = urllib.request.Request(
            TOKEN_URL,
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))

    def fetch_userinfo(self, access_token: str) -> dict[str, object]:
        request = urllib.request.Request(
            USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            value = json.loads(response.read().decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("UserInfo gaf geen JSON-object terug.")
        return value

    def logout(self, _parsed: urllib.parse.ParseResult) -> None:
        session_id, _session = self.current_session()
        if session_id:
            SESSIONS.pop(session_id, None)
        expired = "lab_session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0"
        self.redirect("/", expired)

    def health(self, _parsed: urllib.parse.ParseResult) -> None:
        body = b"ok\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print("BluePeak OIDC lab client listening on 0.0.0.0:8080", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8080), OIDCHandler).serve_forever()
