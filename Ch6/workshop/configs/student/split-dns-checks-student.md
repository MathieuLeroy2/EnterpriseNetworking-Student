# Ch6 student - Split DNS checks

Gebruik deze checks met VM2 als subnet router.

De lokale DNS-server staat op `10.20.0.1`.

## 1. Eerst IP testen

```text
curl -kI https://10.20.10.4
```

| Test | Verwacht | Werkelijk |
|---|---|---|
| HTTPS via IP | werkt | ... |

Als dit niet werkt, los eerst routing, ACL of service op.

## 2. DNS testen

```text
nslookup netbox.voltlab.lan
```

| Veld | Waarde |
|---|---|
| DNS-server gebruikt | ... |
| resolved IP | ... |
| verwacht IP | `10.20.10.4` |

## 3. Hostname testen

```text
curl -kI https://netbox.voltlab.lan
```

| Test | Verwacht | Werkelijk |
|---|---|---|
| HTTPS via hostname | werkt | ... |

## 4. Reflectie

Beantwoord:

- Waarom test je eerst via IP?
- Wat doet Split DNS?
- Wat is het verschil met MagicDNS?
- Waarom moet DNS naar `10.20.0.1` via Tailscale kunnen?
