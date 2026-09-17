# Ch7 student - quick tests

Gebruik deze testen als checklist.

## Setup

| Test | Commando | Verwacht |
|---|---|---|
| daemon | `systemctl is-active tailscaled` | `active` |
| overlay-IP | `tailscale ip -4` | `100.x.x.x` |
| interface | `ip -br address show tailscale0` | interface aanwezig |
| peers | `tailscale status` | laptop en VM zichtbaar |
| HTTP-listener | `ss -lntp \| grep ':8080'` | alleen Tailscale-IP |
| throughputlistener | `ss -lntp \| grep ':5201'` | alleen Tailscale-IP |

## Per fysiek netwerk

Voer op Devbit en eduroam/campusroam uit:

```text
tailscale netcheck
tailscale ping --c 10 --until-direct=false <VM>
tailscale status
curl.exe http://<VM-TAILSCALE-IP>:8080
```

| Controle | Geldige uitkomst |
|---|---|
| UDP | true of false, correct geïnterpreteerd |
| eerste ping | vaak DERP, maar niet verplicht |
| stabiel pad | direct, relay of peer-relay |
| HTTP via Tailscale | werkt |
| HTTP via Devbit-IP vanaf campusroam | faalt verwacht |

## Security

| Test | Verwacht |
|---|---|
| TCP/8081 op Tailscale-IP | faalt |
| Tailscale-client tijdelijk uit | Tailscale-IP faalt |
| capture op `tailscale0` | inner HTTP zichtbaar |
| capture op fysieke interface | buitenste transport en metadata, geen leesbare HTTP-marker |
| gewone internetroute | lokale default route, omdat geen exit node actief is |
| HTTP via MagicDNS-naam | werkt als MagicDNS actief is; anders afzonderlijk verklaren |

## Interpretatiecheck

Je conclusie bevat:

- NAT en firewall zijn verschillende functies;
- endpoint discovery is niet hetzelfde als data relayeren;
- direct verkeer gebruikt UDP;
- DERP is een end-to-end versleutelde fallback;
- relay is vooral een performance- en metadatavraag;
- VPN-encryptie vervangt ACL, host firewall en applicatieauthenticatie niet;
- geen router- of switchwijziging was nodig.
