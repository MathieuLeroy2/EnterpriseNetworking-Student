# Ch7 student - meetblad

Gebruik dit blad tijdens de workshop. Redacteer publieke IP-adressen in je indiening.

## Identiteit en adressen

| Eigenschap | Waarde |
|---|---|
| VM-hostname | ... |
| VM Devbit-interface | ... |
| VM Devbit-IP | ... |
| VM Tailscale-IP | ... |
| VM MagicDNS-naam | ... |
| laptop device name | ... |
| laptop Tailscale-IP | ... |
| Tailscale-versie VM | ... |
| Tailscale-versie laptop | ... |

## Underlayvergelijking

| Meetpunt | Devbit | eduroam/campusroam |
|---|---|---|
| lokaal laptop-IP | ... | ... |
| default gateway | ... | ... |
| publiek endpoint, geredigeerd | ... | ... |
| laptop Tailscale-IP | ... | ... |
| VM Tailscale-IP | ... | ... |

## `tailscale netcheck`

| Veld | Devbit | eduroam/campusroam | Interpretatie |
|---|---|---|---|
| UDP | ... | ... | ... |
| IPv4 | ... | ... | ... |
| IPv6 | ... | ... | ... |
| MappingVariesByDestIP | ... | ... | ... |
| PortMapping | ... | ... | ... |
| Nearest DERP | ... | ... | ... |
| latency nearest DERP | ... | ... | ... |

## Pad en latency

| Meetpunt | Devbit | eduroam/campusroam |
|---|---|---|
| eerste `tailscale ping`-pad | ... | ... |
| stabiele pad | ... | ... |
| `tailscale status` connection type | ... | ... |
| directe endpoint, geredigeerd | ... | ... |
| gemiddelde/typische latency | ... | ... |

## Applicatie en throughput

| Test | Devbit | eduroam/campusroam |
|---|---|---|
| HTTP via Tailscale-IP:8080 | ... | ... |
| HTTP via Devbit-IP:8080 | ... | ... |
| `iperf3` laptop naar VM | ... | ... |
| `iperf3 -R` VM naar laptop | ... | ... |
| connection type tijdens transfer | ... | ... |

## Packet capture

| Capturepunt | Buitenste adressen/poorten | HTTP-marker zichtbaar? | Betekenis |
|---|---|---|---|
| `tailscale0` | ... | ... | ... |
| fysieke Devbit-interface | ... | ... | ... |

## Positieve en negatieve tests

| Test | Verwacht | Werkelijk | Verklaring |
|---|---|---|---|
| Tailscale-IP:8080 met Tailscale actief | werkt | ... | ... |
| Devbit-IP:8080 vanaf campusroam | faalt | ... | ... |
| Tailscale-IP:8081 | faalt | ... | ... |
| Tailscale-IP:8080 met Tailscale uit | faalt | ... | ... |

## DNS

| Test | Resultaat | Interpretatie |
|---|---|---|
| MagicDNS-naam naar Tailscale-IP | ... | ... |
| HTTP via MagicDNS-naam | ... | ... |
| gebruikte resolver | ... | ... |
| mogelijke naammetadata voor lokaal netwerk | ... | ... |

## Eindconclusie in vijf zinnen

1. De underlay veranderde doordat ...
2. De overlay bleef ...
3. NAT traversal leverde ...
4. De VPN beschermde ..., terwijl metadata zoals ... zichtbaar bleef.
5. Mijn infrastructuuradvies is ...
