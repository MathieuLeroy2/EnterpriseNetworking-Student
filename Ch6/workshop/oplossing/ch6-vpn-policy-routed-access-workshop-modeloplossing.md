# Workshop 6 - VPN policy en routed access met Tailscale

## Modeloplossing voor studenten

## 1. Korte samenvatting

De student werkte in een persoonlijke, student-managed tailnet.

VM1 werd als serverdevice behandeld en kreeg een tag zoals `tag:student-vm` of `tag:webserver`.

Na heraanmelding met een eigen tijdelijke auth key werd de tag automatisch toegepast.

De ACL liet alleen noodzakelijke toegang toe, bijvoorbeeld HTTP naar de webserver.

Tailscale SSH werd apart getest en beperkt via SSH-policy.

Een brede ACL werd herkend als gevaarlijk.

Met VM2 gaf de subnet router gecontroleerde toegang tot het labsubnet `10.20.0.0/16`.

De student bereikte NetBox als bestaande interne HTTPS-dienst op `10.20.10.4`, zonder toegang tot de NetBox-VM zelf.

Split DNS liet `netbox.voltlab.lan` oplossen via `10.20.0.1`.

De student sloot af met audit en cleanup.

---

## 2. Voorbeeldinventaris

| Item | Voorbeeldwaarde |
|---|---|
| Tailnet | persoonlijk / student-managed |
| Student user | `<student-login-email>` |
| Student device | `student-laptop` |
| VM1 hostname | `bp-ch6-s01` |
| VM1 Tailscale-IP | `100.x.x.x` |
| VM1 intern IP | DHCP-IP, tijdens de oefening genoteerd |
| VM1 tag | `tag:student-vm`, `tag:webserver` |
| VM2 subnet router | `bp-ch6-r01` |
| VM2 intern IP | DHCP-IP, tijdens de oefening genoteerd |
| Intern subnet | `10.20.0.0/16` |
| DNS-server | `10.20.0.1` |
| NetBox HTTPS-dienst | `10.20.10.4`, `netbox.voltlab.lan` |

---

## 3. Tags

Sterke conclusie:

> VM1 is geen gewoon user-owned device meer. Door de tag wordt ze als serverrol behandeld. Policy kan nu naar `tag:webserver` of `tag:student-vm` verwijzen in plaats van naar een persoonlijke eigenaar.

Tag ownership:

> In deze student-tailnet mag `autogroup:admin` de labtags toekennen. In een echte organisatie zou dat beperkt worden tot een kleine beheerrol, want wie tags mag toekennen, kan devices in een serverrol plaatsen.

---

## 4. Auth key

Voorbeeldcommand met placeholder:

```text
sudo tailscale up --auth-key=<AUTH-KEY> --hostname=bp-ch6-s01
```

Goed verslag:

- vermeldt dat een auth key gebruikt werd;
- vermeldt welke tag automatisch verscheen;
- vermeldt dat de key niet opgenomen werd;
- toont `tailscale status` zonder secrets.

Fout verslag:

- bevat een volledige auth key;
- bevat een loginlink;
- bevat een screenshot met key.

---

## 5. ACL voor alleen HTTP

Voorbeeld:

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "dst": ["tag:webserver:80"]
}
```

Verwachte tests:

| Test | Verwacht |
|---|---|
| `curl -I http://<vm1-tailscale-ip>` | werkt |
| `nc -vz <vm1-tailscale-ip> 22` | faalt |
| `nc -vz <vm1-tailscale-ip> 443` | faalt tenzij toegestaan |

Conclusie:

> De ACL geeft alleen HTTP-toegang. Andere poorten werken niet omdat er geen allow-regel voor bestaat.

---

## 6. Tailscale SSH

Verwacht:

```text
tailscale ssh debian@<vm1-name>
```

werkt alleen als de SSH-policy dit toelaat.

Klassieke SSH:

```text
ssh debian@<vm1-tailscale-ip>
```

werkt niet automatisch.

Conclusie:

> Tailscale SSH wordt via de tailnet policy geregeld. Dat is niet hetzelfde als TCP/22 openzetten.

---

## 7. Brede ACL

Foute regel:

```json
{
  "action": "accept",
  "src": ["*"],
  "dst": ["*:*"]
}
```

Analyse:

- elke bron is toegestaan;
- elke bestemming is toegestaan;
- elke poort is toegestaan;
- laterale beweging wordt mogelijk;
- negatieve tests verliezen betekenis;
- oude devices kunnen te veel bereiken.

Verbetering:

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "dst": ["tag:webserver:80"]
}
```

---

## 8. Subnet router

VM1 blijft het directe Tailscale-testdoel.

Voor routed access wordt NetBox gebruikt als bestaande HTTPS-dienst in het labnet.

Studenten krijgen geen shell- of admintoegang tot NetBox.

VM2 adverteert:

```text
10.20.0.0/16
```

Minimale ACL:

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "dst": ["10.20.10.4:443"]
}
```

Verwachte test via VM2:

```text
curl -kI https://10.20.10.4
```

Verwacht resultaat:

```text
HTTP/1.1 200 OK
```

Negatieve tests:

| Test | Verwacht |
|---|---|
| `nc -vz 10.20.10.4 22` | faalt |
| `nc -vz 10.20.0.1 22` | faalt |
| toegang tot willekeurige host | faalt of geen host |

Conclusie:

> NetBox draait niet zelf in de tailnet. De route via VM2 bestaat, maar ACLs beperken de bruikbare toegang tot `10.20.10.4:443`.

Brede routed ACL:

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "dst": ["10.20.0.0/16:*"]
}
```

Waarom fout:

- het volledige subnet wordt bereikbaar;
- alle poorten worden bereikbaar;
- SSH naar `10.20.10.4:22` zou niet langer bewust geblokkeerd zijn;
- NetBox, de DNS-server en andere labhosts kunnen onbedoeld beheerdoelen worden.

---

## 9. Split DNS

Verwachte test met VM2:

```text
nslookup netbox.voltlab.lan
curl -kI https://netbox.voltlab.lan
```

Verwacht:

| Test | Verwacht |
|---|---|
| DNS | `netbox.voltlab.lan` lost op naar `10.20.10.4` |
| HTTPS | NetBox antwoordt |

Conclusie:

> Split DNS stuurt vragen voor `voltlab.lan` naar de interne DNS-server via de Tailscale-route. MagicDNS is voor tailnet-devices; Split DNS is voor interne domeinen.

---

## 10. Exit node policy

Sterke uitleg:

> Een subnet router geeft toegang tot private subnetten zoals `10.20.0.0/16`. Een exit node stuurt internetverkeer via een tailnet-device naar buiten. Daarom horen ze een andere policy te krijgen.

Privacyreflectie:

> Exit node gebruik kan metadata over internetverkeer zichtbaar maken voor de beheerder van de exit node. Daarom moet duidelijk zijn wie exit nodes mag gebruiken en wat gelogd wordt.

---

## 11. Audit en cleanup

Minimale checklist:

| Controle | Verwacht |
|---|---|
| VM1 herkenbaar | ja |
| VM1 correct getagd in directe fase | ja |
| VM2 routeert `10.20.0.0/16` | ja |
| NetBox via `10.20.10.4:443` bereikbaar | ja |
| geen shell- of admintoegang tot NetBox gebruikt | ja |
| auth key niet in verslag | ja |
| `*:*` niet permanent aanwezig | ja |
| HTTP-only ACL getest | ja |
| Tailscale SSH beperkt | ja |
| route `10.20.0.0/16` bewust | ja |
| SSH naar `10.20.10.4:22` faalt | ja |
| Split DNS werkt | ja |
| oude devices verwijderd of gemeld | ja |

---

## 12. Eindantwoord

Zelfde tailnet is geen voldoende securitybeleid.

Een tailnet maakt private connectiviteit mogelijk, maar zonder policy kan die connectiviteit te breed zijn.

Ook in een persoonlijke student-tailnet kan een oude VM, brede ACL, foutieve tag of onnodige route te veel toegang geven.

Een subnet route is ook geen vrijgeleide. VM2 mag een route naar `10.20.0.0/16` aanbieden, maar policy moet nog altijd bepalen welke IP's en poorten bruikbaar zijn.

In een professionele omgeving moet toegang afhangen van user, group, device, tag, bestemming, poort, route en context.

Daarom zijn tags, ACLs, SSH-policy, route approval, Split DNS en lifecyclebeheer nodig.
