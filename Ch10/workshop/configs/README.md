# Ch10 workshop configs

Deze map bevat ondersteunende bestanden voor workshop 10.

De workshop combineert:

- Traefik als reverse proxy;
- Authentik core en embedded proxy outpost;
- single-application forward auth;
- afzonderlijke groepsbindings per applicatie;
- step-up TOTP voor het adminportaal;
- een publieke route zonder login;
- demoapps die geselecteerde identity-headers tonen;
- positieve, negatieve, spoofing- en fail-closedtests.

Studenten werken in:

```text
student/identity-aware-lab
```

De studentversie bevat een volledige containerstack, maar alleen starterroutes voor
Authentik en de publieke app. Studenten bouwen de protected routes en
forward-authconfiguratie zelf op.

Docenten vinden in `teacher/`:

- de finale Traefik-configuratie;
- verwachte Authentik-objecten en bindings;
- snelle verwachte testresultaten.

## Versies

- Authentik: `2026.5.3`, gelijk aan hoofdstuk 9;
- Traefik: `v3.1`, gelijk aan hoofdstuk 8;
- PostgreSQL: `16-alpine`;
- demoapps: `python:3.12-alpine`.

Controleer voor een nieuw academiejaar de ondersteunde versies, release notes en
eventuele gewijzigde UI-menunamen.

## Secrets

`.env.example` bevat alleen placeholders.

Nooit delen:

- `.env`;
- `AUTHENTIK_SECRET_KEY`;
- databasewachtwoord;
- browsercookies;
- tokens;
- TOTP-seed, QR-code of herstelcodes;
- echte productiedomeinen of klantgegevens.

## Veiligheidskeuzes

- Alleen Traefik publiceert hostpoorten.
- Backends en Authentik core blijven op het interne Docker-netwerk.
- De Docker socket wordt niet gemount.
- De outpostroute is afzonderlijk en heeft hogere prioriteit.
- De admin-MFA-blueprint bevat geen gebruikers of secrets.
- HTTP is uitsluitend voor lokale didactische hostnames.

## Officiële referenties

Technische keuzes werden op 18 augustus 2026 gecontroleerd tegen:

- [Authentik forward auth](https://docs.goauthentik.io/add-secure-apps/providers/proxy/forward_auth)
- [Authentik met Traefik](https://docs.goauthentik.io/add-secure-apps/providers/proxy/server_traefik/)
- [Proxy provider maken](https://docs.goauthentik.io/add-secure-apps/providers/proxy/create-proxy-provider/)
- [Embedded outpost](https://docs.goauthentik.io/add-secure-apps/outposts/embedded/)
- [Authenticator Validation stage](https://docs.goauthentik.io/add-secure-apps/flows-stages/stages/authenticator_validate/)

