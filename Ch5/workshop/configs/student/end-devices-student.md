# Ch5 student - Debian VM, account en IP-plan

Vul deze gegevens tijdens de workshop aan.

## Tailscale-account

| Item | Waarde |
|---|---|
| Eigen Tailscale-account gebruikt? | ja/nee |
| Accounttype | schoolaccount/persoonlijk |
| Tailnetnaam | ... |
| VM zichtbaar in eigen tailnet? | ja/nee |
| Testclient zichtbaar in eigen tailnet? | ja/nee |

Neem geen loginlinks, tokens of auth keys op.

## Eigen VM

| Item | Waarde |
|---|---|
| Studentnaam of duo | ... |
| VM-hostname | ... |
| VM-netwerkinterface | ... |
| VM-IP | ... |
| Default gateway | ... |
| Tailscale-interface | `tailscale0` na installatie |
| Tailscale-IP | `100.x.x.x` na installatie |
| MagicDNS-naam | ... |
| Webserver | nginx/apache/andere |
| Firewalllocatie | Proxmox |

## Testclient

| Client | Rol | Wifi/netwerk | IP op dat netwerk | Tailscale-IP | Opmerking |
|---|---|---|---|---|---|
| Laptop op Devbit | directe test | Devbit | ... | ... | VM-IP testen |
| Laptop op eduroam | gescheiden netwerk | eduroam | ... | ... | VM-IP en Tailscale-IP testen |
| Debian VM | server | Proxmox/Devbit-zijde | ... | ... | HTTP-server |

## Verwachte poorten

| Poort | Dienst | Direct naar VM-IP | Via Tailscale-IP | Opmerking |
|---:|---|---|---|---|
| TCP 80 | HTTP webserver | geblokkeerd | werkt | hoofdcase |

## Paden

| Pad | Verwacht |
|---|---|
| Devbit naar VM-IP:80 | faalt |
| eduroam naar VM-IP:80 | faalt |
| eduroam + Tailscale naar Tailscale-IP:80 | werkt |
| eduroam + exit node via VM | publiek IP wordt Devbit |
