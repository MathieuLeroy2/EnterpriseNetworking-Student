# Ch6 student - audit en cleanup

Gebruik deze checklist op het einde.

| Controle | Ja/nee | Opmerking |
|---|---|---|
| Alle devices herkenbaar | ... | ... |
| VM1 was eerst correct getagd | ... | ... |
| VM2 is subnet router voor `10.20.0.0/16` | ... | ... |
| VM1 en VM2 DHCP-IP's genoteerd | ... | ... |
| NetBox via `10.20.10.4:443` getest | ... | ... |
| Geen shell- of admintoegang tot NetBox gebruikt | ... | ... |
| Auth key niet opgenomen in verslag | ... | ... |
| Loginlink niet opgenomen in verslag | ... | ... |
| HTTP-only ACL positief getest | ... | ... |
| SSH/andere poorten negatief getest | ... | ... |
| Tailscale SSH apart getest | ... | ... |
| Brede ACL herkend en verbeterd | ... | ... |
| Subnet router via IP getest | ... | ... |
| SSH naar `10.20.10.4:22` faalt | ... | ... |
| SSH naar `10.20.0.1:22` faalt | ... | ... |
| Split DNS getest | ... | ... |
| Exit node policy begrepen | ... | ... |
| Oude of foute devices gemeld | ... | ... |

Korte eindreflectie:

```text
Zelfde tailnet is geen voldoende securitybeleid, zelfs in mijn persoonlijke tailnet, omdat ...
```
