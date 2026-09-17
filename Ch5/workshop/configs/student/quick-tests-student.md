# Ch5 student - quick tests

Gebruik deze testen als checklist.

## Account en devices

| Test | Bron | Doel | Verwacht | Interpretatie |
|---|---|---|---|---|
| Account | student | Tailscale login | eigen account actief | persoonlijke tailnet |
| VM zichtbaar | testclient | `tailscale status` | VM staat in lijst | beide devices zitten in dezelfde tailnet |
| Testclient zichtbaar | VM | `tailscale status` | testclient staat in lijst | peerrelatie werkt |

## Beginsituatie

| Test | Bron | Doel | Verwacht | Interpretatie |
|---|---|---|---|---|
| Webserver lokaal | VM | `curl -I http://127.0.0.1` | werkt | applicatie draait |
| Direct HTTP Devbit | Devbit-client | `http://<VM-IP>` | faalt | Proxmox-firewall blokkeert HTTP |
| Direct HTTP eduroam | eduroam-client | `http://<VM-IP>` | faalt | ander netwerk en/of firewall |

## Tailscale

| Test | Bron | Doel | Verwacht | Interpretatie |
|---|---|---|---|---|
| Tailscale-IP | VM | `tailscale ip -4` | `100.x.x.x` | VM heeft overlayadres |
| Interface | VM | `ip -br addr show tailscale0` | interface zichtbaar | VPN-interface bestaat |
| Peer ping | testclient | `tailscale ping <vm-name>` | werkt | overlayconnectiviteit |

## HTTP via Tailscale

| Test | Bron | Doel | Verwacht | Interpretatie |
|---|---|---|---|---|
| HTTP via Tailscale-IP | eduroam + Tailscale | `http://100.x.x.x` | werkt | webdienst via VPN |
| HTTP via MagicDNS | eduroam + Tailscale | `http://<vm-name>` | werkt | naamresolutie |
| HTTP direct via VM-IP | eduroam zonder Tailscale-pad | `http://<VM-IP>` | faalt | direct pad blijft dicht |

## Challenge: exit node via Devbit

| Test | Bron | Doel | Verwacht | Interpretatie |
|---|---|---|---|---|
| Publiek IP zonder exit node | eduroam | `curl https://ifconfig.me` | eduroam-public-IP | normaal internetpad |
| Publiek IP met VM als exit node | eduroam + Tailscale | `curl https://ifconfig.me` | Devbit-public-IP | full tunnel via VM |

## Sterke eindconclusie

Een sterke eindconclusie bevat:

- eigen Tailscale-account gebruikt;
- VM en testclient zitten in dezelfde persoonlijke tailnet;
- directe HTTP via Devbit faalt;
- directe HTTP via eduroam faalt;
- HTTP via Tailscale werkt;
- exit node is correct onderscheiden van HTTP-toegang via tailnet.
