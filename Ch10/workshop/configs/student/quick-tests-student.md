# Ch10 - Snelle testmatrix student

Vul alleen resultaten en veilig bewijs in. Kopieer geen cookies, tokens, wachtwoorden
of TOTP-gegevens.

## Basis

| Test | Verwacht | Werkelijk |
|---|---|---|
| alle negen services bestaan | ja | ... |
| Traefik luistert op `8100` | ja | ... |
| dashboard op `8188` | ja | ... |
| Authentik via `auth.bluepeak.test` | ja | ... |
| public zonder login | allow | ... |

## Outpost

| Hostname + `/outpost.goauthentik.io/ping` | Verwacht | Werkelijk |
|---|---|---|
| intranet | 204 | ... |
| monitoring | 204 | ... |
| admin | 204 | ... |
| partner | 204 | ... |

## Toegang

| Identiteit | Intranet | Monitoring | Admin | Partner |
|---|---|---|---|---|
| Alice | allow | deny | deny | deny |
| Bob | allow | allow | allow na TOTP | deny |
| Eva | deny | deny | deny | allow |

## Security

| Test | Verwacht | Werkelijk |
|---|---|---|
| zelfgekozen `X-authentik-username` zonder sessie | geen bypass | ... |
| directe poorten `8101` tot `8104` | falen | ... |
| onbekende hostname | geen interne app | ... |
| Authentik down, public | werkt | ... |
| Authentik down, nieuwe protected request | fail-closed | ... |

