# Ch6 student - Tailscale policy checks

## 1. Tags

| Vraag | Antwoord |
|---|---|
| Is VM1 user-owned of tagged? | ... |
| Welke tag heeft VM1? | ... |
| Waarom hoort een server getagd te zijn? | ... |
| Wie mag de tag toekennen? | ... |

## 2. Auth key

| Controle | Resultaat |
|---|---|
| VM1 uitgelogd met `sudo tailscale logout` | ... |
| VM1 opnieuw aangemeld met auth key | ... |
| key niet gedocumenteerd | ... |
| automatische tag toegepast | ... |

Gebruik in je verslag alleen:

```text
sudo tailscale up --auth-key=<AUTH-KEY> --hostname=<VM-NAME>
```

## 3. ACL lezen

Voorbeeld:

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "dst": ["tag:webserver:80"]
}
```

Vul in:

| Onderdeel | Betekenis |
|---|---|
| `src` | ... |
| `dst` | ... |
| `80` | ... |
| wat ontbreekt | ... |

## 4. Brede ACL

Waarom is dit gevaarlijk?

```json
{
  "action": "accept",
  "src": ["*"],
  "dst": ["*:*"]
}
```

Antwoord:

```text
...
```

Least-privilege alternatief:

```json
...
```
