# Workshop 5 - HTTP bereikbaar maken via Tailscale

## Modeloplossing voor studenten

## 1. Korte samenvatting

De Debian VM bevat een webserver die lokaal werkt.

Directe HTTP naar het gewone VM-IP is geblokkeerd door de Proxmox-firewall.

De student gebruikt een eigen Tailscale-account.

De VM en de laptop/testclient zitten in dezelfde persoonlijke tailnet.

Daardoor wordt de webserver bereikbaar via het Tailscale-IP van de VM, terwijl direct HTTP naar het VM-IP geblokkeerd blijft.

Kernconclusie:

> De service wordt niet publiek opengezet. Ze wordt bereikbaar via een private tailnet van de student.

---

## 2. VM- en accountinventaris

Voorbeeld:

| Item | Waarde |
|---|---|
| Hostname | `bp-vpn-s07` |
| VM-IP | `10.x.x.x` |
| Tailscale-account | eigen studentaccount |
| Tailnet | persoonlijke tailnet |
| Tailscale-interface | `tailscale0` |
| Tailscale-IP | `100.x.x.x` |
| MagicDNS-naam | `bp-vpn-s07` |
| Webserver | `nginx` |
| Firewalllocatie | Proxmox |

Controlecommands:

```text
hostname
ip -br addr
ip route
tailscale status
tailscale ip -4
```

---

## 3. Webserver lokaal

Test:

```text
curl -I http://127.0.0.1
```

Verwacht resultaat:

```text
HTTP/1.1 200 OK
```

Conclusie:

> De webapplicatie werkt lokaal. Het bereikbaarheidsprobleem zit dus niet bij de webserver zelf.

---

## 4. Directe HTTP-tests

Vanaf Devbit:

```text
curl -I http://<VM-IP>
```

Verwacht:

- faalt door de Proxmox-firewall.

Vanaf eduroam:

```text
curl -I http://<VM-IP>
```

Verwacht:

- faalt door netwerksegmentatie en/of firewall.

Conclusie:

> Direct HTTP naar het VM-IP is niet beschikbaar.

---

## 5. Tailscale-installatie

Voorbeeldinstallatie op de VM:

```text
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

De student meldt aan met het eigen Tailscale-account.

De laptop/testclient wordt met hetzelfde account aangemeld.

Controle:

```text
tailscale status
tailscale ip -4
ip -br addr show tailscale0
```

Verwacht:

- VM staat online in de persoonlijke tailnet;
- laptop/testclient staat ook in dezelfde tailnet;
- VM heeft een `100.x.x.x`-adres;
- interface `tailscale0` bestaat.

---

## 6. HTTP via Tailscale

Test vanaf de laptop/testclient op eduroam:

```text
curl -I http://100.x.x.x
```

Of met MagicDNS:

```text
curl -I http://bp-vpn-s07
```

Verwacht:

```text
HTTP/1.1 200 OK
```

Conclusie:

> HTTP werkt via de Tailscale-overlay.

---

## 7. Testtabel

| Test | Verwacht | Werkelijk | Conclusie |
|---|---|---|---|
| HTTP lokaal op VM | werkt | werkt | webserver ok |
| Devbit naar VM-IP | faalt | faalt | Proxmox-firewall |
| eduroam naar VM-IP | faalt | faalt | apart netwerk/firewall |
| Tailscale status | VM en laptop zien elkaar | werkt | zelfde tailnet |
| Tailscale ping | werkt | werkt | overlay ok |
| HTTP via Tailscale-IP | werkt | werkt | VPN-only toegang |
| HTTP via MagicDNS | werkt indien actief | werkt | naamresolutie ok |

---

## 8. Analyse

De oplossing werkt omdat er drie verschillende paden zijn.

```text
Devbit client  --X-->  VM-IP:80

eduroam client --X-->  VM-IP:80

eduroam client + Tailscale  -->  Tailscale-IP:80
```

De Proxmox-firewall ziet en filtert directe toegang naar het VM-IP.

Tailscale bouwt een overlay tussen devices die in dezelfde persoonlijke tailnet zitten.

De HTTP-service wordt dus niet publiek geopend.

Kernzin:

> Tailscale geeft een tweede privaat toegangspad naast het campusnetwerk.

---

## 9. Challenge 1: MagicDNS

Een sterke studentoplossing test niet alleen op Tailscale-IP, maar ook op naam.

Voorbeeld:

```text
curl -I http://bp-vpn-s07
```

Verwacht:

```text
HTTP/1.1 200 OK
```

Conclusie:

> MagicDNS maakt de test beheerbaarder. Als het Tailscale-IP werkt maar de naam niet, ligt het probleem waarschijnlijk bij naamresolutie of device naming.

---

## 10. Challenge 2: devicebeheer

Een sterke studentoplossing vermeldt ook de eigen Tailscale-inventaris.

Voorbeeld:

| Device | Rol | Opmerking |
|---|---|---|
| `bp-vpn-s07` | Debian VM | webserver |
| `laptop-mathieu` | testclient | Devbit/eduroam tests |

Sterke conclusie:

> De VM en laptop staan in dezelfde persoonlijke tailnet. Oude of onbekende devices moeten na de workshop verwijderd worden.

---

## 11. Challenge 3: exit node via Devbit

Als de VM op Devbit als exit node wordt gebruikt:

```text
sudo tailscale up --advertise-exit-node
```

Daarna keurt de student de exit node goed in de eigen Tailscale admin console.

Vanaf de laptop op eduroam:

```text
curl https://ifconfig.me
```

Verwacht:

| Situatie | Publiek IP |
|---|---|
| zonder exit node | eduroam-IP |
| met VM als exit node | Devbit-IP |

Conclusie:

> De exit node demonstreert full tunnel. Dit is niet nodig om HTTP naar de VM via Tailscale te bereiken.

---

## 12. Risicoanalyse

| Risico | Impact | Maatregel |
|---|---|---|
| Verkeerd account gebruikt | VM en laptop zien elkaar niet | zelfde account controleren |
| Elk device in tailnet mag HTTP | te brede toegang | devicebeheer en cleanup |
| Webapp heeft geen login | VPN-gebruiker ziet alles | app-authenticatie toevoegen |
| Oude VM blijft in tailnet | vergeten toegang | device verwijderen na workshop |
| MagicDNS-verwarring | verkeerde host getest | device-inventaris |
| Gestolen account | onbevoegde tailnettoegang | MFA en device removal |
| Exit node onbedoeld actief | verkeer loopt via VM/Devbit | exit node uitschakelen na demo |

---

## 13. Eindconclusie

De VM had een werkende lokale webserver.

Directe HTTP naar het VM-IP werkte niet vanaf Devbit door de Proxmox-firewall.

Directe HTTP naar het VM-IP werkte ook niet vanaf eduroam.

De student gebruikte een eigen Tailscale-account en meldde zowel de VM als de laptop aan in dezelfde persoonlijke tailnet.

Daarna werkte HTTP via het Tailscale-IP of MagicDNS.

De webdienst werd dus niet publiek of campusbreed geopend.

Eindantwoord:

> HTTP via Tailscale bereikbaar maken is iets anders dan HTTP publiek openzetten. De service blijft onbereikbaar via het gewone VM-IP, maar wordt bereikbaar via een geauthenticeerde private overlay waarin alleen devices uit dezelfde tailnet deelnemen.
