# Workshop 6 - VPN policy en routed access met Tailscale

## 1. Situering

In Ch5 maakte je een webserver bereikbaar via Tailscale.

Je bewees toen vooral dat connectiviteit werkt.

In deze workshop onderzoek je iets anders:

> Werkt alleen de toegang die nodig is?

Je werkt in je eigen persoonlijke tailnet. Je behandelt die tailnet als een kleine organisatie. Je beheert dus zelf devices, tags, auth keys, ACLs, Tailscale SSH, subnet routes, Split DNS en cleanup.

Belangrijk:

> Een VPN die werkt, is niet automatisch veilig of goed ontworpen.

---

## 2. Scenario

BluePeak Services gebruikt Tailscale voor remote access.

Het bedrijf heeft:

- een laptop van een medewerker;
- een eigen oefenserver `VM1`;
- een routerserver `VM2` die als subnet router werkt;
- een bestaand intern labnet `10.20.0.0/16`;
- een bestaande NetBox-server op `10.20.10.4`;
- een lokale DNS-server op `10.20.0.1`;
- een interne DNS-naam `netbox.voltlab.lan`;
- de eis dat alleen noodzakelijke toegang openstaat.

VM1 en VM2 krijgen hun gewone lab-IP via DHCP. Je noteert die adressen tijdens de oefening.

NetBox is geen VM die jij beheert. Je krijgt geen shelltoegang tot NetBox. Je gebruikt NetBox alleen als interne HTTPS-dienst om routed access en Split DNS te testen.

De organisatie wil niet:

> Elk device in de tailnet mag automatisch naar elk ander device of elk intern IP.

---

## 3. Beginsituatie

Je hebt deze toestellen en diensten:

| Onderdeel | Rol | IP-adres |
|---|---|---|
| Laptop | Tailscale-client en testtoestel | eigen Tailscale-IP |
| VM1 | eigen oefenserver | DHCP-adres tijdens de oefening |
| VM2 | subnet router | DHCP-adres tijdens de oefening |
| Labnet | intern subnet achter VM2 | `10.20.0.0/16` |
| Lokale DNS-server | resolver voor `voltlab.lan` | `10.20.0.1` |
| NetBox | bestaande interne HTTPS-dienst | `10.20.10.4` |
| NetBox hostname | interne DNS-naam | `netbox.voltlab.lan` |

Je gebruikt:

- terminal;
- browser;
- Tailscale admin console;
- `curl`;
- `nslookup` of `dig`;
- `nc` of `ncat`;
- de configbijlagen in `Ch6/workshop/configs/student/`.

Veiligheidsregel:

> Noteer nooit auth keys, loginlinks, tokens, recovery codes of wachtwoorden in je verslag.

---

## 4. Doelen

Na deze workshop kan je:

1. uitleggen waarom "zelfde tailnet" geen voldoende securitybeleid is;
2. user-owned devices en tagged devices herkennen;
3. tag owners instellen voor labtags;
4. VM1 opnieuw aanmelden met een tagged auth key;
5. een ACL schrijven die alleen HTTP naar VM1 toelaat;
6. bewijzen dat klassieke SSH op TCP/22 niet zomaar werkt;
7. Tailscale SSH apart testen en vergelijken met klassieke SSH;
8. VM2 als subnet router gebruiken;
9. een route naar `10.20.0.0/16` adverteren en goedkeuren;
10. HTTPS naar NetBox op `10.20.10.4:443` toelaten;
11. aantonen dat SSH naar NetBox niet bereikbaar is;
12. Split DNS testen voor `netbox.voltlab.lan`;
13. brede regels zoals `10.20.0.0/16:*` herkennen en verbeteren;
14. audit en cleanup uitvoeren zonder secrets te lekken.

---

## 5. Topologie

Deze workshop heeft twee delen.

### 5.1 Directe toegang naar VM1

```text
Laptop
  |
  | Tailscale
  v
VM1
tag:student-vm
tag:webserver
```

In dit deel test je device access. VM1 is zelf een Tailscale-device.

### 5.2 Routed access naar het interne labnet

```text
Laptop
  |
  | Tailscale
  v
VM2
tag:subnet-router
advertise route 10.20.0.0/16
  |
  | intern labnet
  v
DNS     10.20.0.1
NetBox  10.20.10.4
```

In dit deel test je routed access. NetBox draait niet in jouw tailnet en is geen VM waar je op inlogt. Je bereikt alleen de HTTPS-pagina's via VM2.

Controlepunt:

> Kan je uitleggen wat het verschil is tussen VM1 rechtstreeks bereiken via Tailscale en NetBox bereiken via VM2 als subnet router?

---

## 6. Werkwijze

Werk in deze volgorde:

1. inventariseer laptop, VM1 en VM2;
2. test directe Tailscale-toegang naar VM1;
3. definieer tags en tag owners;
4. meld VM1 opnieuw aan met een tagged auth key;
5. beperk directe toegang tot HTTP op VM1;
6. test Tailscale SSH en klassieke SSH;
7. configureer VM2 als subnet router;
8. keur de route `10.20.0.0/16` goed;
9. laat alleen HTTPS naar NetBox toe;
10. test dat SSH naar NetBox faalt;
11. analyseer een brede routed ACL;
12. configureer en test Split DNS;
13. open NetBox via de interne hostname;
14. voer audit en cleanup uit.

Pas niet zomaar alles tegelijk aan. Test na elke stap wat veranderd is.

---

## 7. Stap 1: inventariseer je lab

Controleer op je laptop:

```text
tailscale status
tailscale ip -4
```

Controleer op VM1:

```text
hostname
ip -br address
tailscale status
tailscale ip -4
```

Controleer op VM2:

```text
hostname
ip -br address
tailscale status
tailscale ip -4
```

Vul in:

| Item | Waarde |
|---|---|
| Tailnet | ... |
| Laptop device name | ... |
| Laptop Tailscale-IP | ... |
| VM1 hostname | ... |
| VM1 DHCP-IP | ... |
| VM1 Tailscale-IP | ... |
| VM2 hostname | ... |
| VM2 DHCP-IP | ... |
| VM2 Tailscale-IP | ... |
| Intern labnet | `10.20.0.0/16` |
| DNS-server | `10.20.0.1` |
| NetBox IP | `10.20.10.4` |
| NetBox hostname | `netbox.voltlab.lan` |

Controlepunt:

> Je weet welke IP's bij Tailscale horen, welke IP's via DHCP op het labnet komen en welke interne diensten vast zijn.

---

## 8. Stap 2: test directe toegang naar VM1

VM1 staat in deze fase rechtstreeks in Tailscale.

Test HTTP naar VM1 via het Tailscale-IP:

```text
curl -I http://<vm1-tailscale-ip>
```

Test klassieke SSH naar VM1 via het Tailscale-IP:

```text
nc -vz <vm1-tailscale-ip> 22
```

Vul in:

| Test | Verwacht in baseline | Werkelijk |
|---|---|---|
| HTTP naar VM1 Tailscale-IP | werkt als webserver draait en policy dit toelaat | ... |
| TCP/22 naar VM1 Tailscale-IP | afhankelijk van huidige policy | ... |

Beantwoord:

- Bereik je VM1 nu als Tailscale-device of via een subnet router?
- Waarom is dit nog geen bewijs van least privilege?

Controlepunt:

> Je hebt de beginsituatie gemeten voordat je policy strenger maakt.

---

## 9. Stap 3: definieer tags en tag owners

Open de access control policy van je tailnet.

Voeg labtags toe of controleer dat ze bestaan:

```json
"tagOwners": {
  "tag:student-vm": ["autogroup:admin"],
  "tag:webserver": ["autogroup:admin"],
  "tag:ssh-server": ["autogroup:admin"],
  "tag:subnet-router": ["autogroup:admin"]
}
```

Vul in:

| Tag | Bedoeling | Wie mag tag toekennen? |
|---|---|---|
| `tag:student-vm` | VM1 als labserver | ... |
| `tag:webserver` | webdienst op VM1 | ... |
| `tag:ssh-server` | Tailscale SSH-test | ... |
| `tag:subnet-router` | VM2 als subnet router | ... |

Beantwoord:

- Wat betekent `autogroup:admin`?
- Waarom mag niet elk device zomaar `tag:subnet-router` krijgen?

Controlepunt:

> Tags bepalen niet alleen namen, maar ook welke policy op een device van toepassing wordt.

---

## 10. Stap 4: meld VM1 opnieuw aan met een tagged auth key

Maak in je Tailscale admin console een tijdelijke auth key voor VM1.

Gebruik voor VM1 minstens:

- korte expiry;
- bij voorkeur one-off;
- automatische tag `tag:student-vm`;
- eventueel ook `tag:webserver`.

Noteer de key nooit in je verslag.

Op VM1:

```text
sudo tailscale logout
sudo tailscale up --auth-key=<AUTH-KEY> --hostname=<VM1-NAME>
tailscale status
tailscale ip -4
```

Vul in:

| Controle | Resultaat |
|---|---|
| VM1 opnieuw aangemeld | ... |
| VM1 hostname correct | ... |
| VM1 heeft `tag:student-vm` | ... |
| VM1 heeft `tag:webserver` indien gebruikt | ... |
| auth key niet gedocumenteerd | ... |

Beantwoord:

- Wat is het verschil tussen een user-owned VM en een tagged VM?
- Waarom past een tag beter bij een serverrol?

Controlepunt:

> VM1 is nu niet zomaar "jouw VM", maar een device met een serverrol in policy.

---

## 11. Stap 5: laat alleen HTTP naar VM1 toe

Pas je ACL aan zodat leden van je tailnet HTTP naar webservers mogen.

Voorbeeld:

```json
"acls": [
  {
    "action": "accept",
    "src": ["autogroup:member"],
    "dst": ["tag:webserver:80"]
  }
]
```

Test:

```text
curl -I http://<vm1-tailscale-ip>
nc -vz <vm1-tailscale-ip> 22
nc -vz <vm1-tailscale-ip> 443
```

Vul in:

| Test | Verwacht | Werkelijk |
|---|---|---|
| HTTP naar VM1 Tailscale-IP | werkt | ... |
| TCP/22 naar VM1 Tailscale-IP | faalt | ... |
| TCP/443 naar VM1 Tailscale-IP | faalt tenzij bewust toegestaan | ... |

Beantwoord:

- Waar staat in de policy dat HTTP mag?
- Waar staat in de policy dat SSH niet mag?
- Waarom is een negatieve test hier even belangrijk als `curl`?

Controlepunt:

> Je bewijst niet alleen dat HTTP werkt, maar ook dat andere poorten niet zomaar openstaan.

---

## 12. Stap 6: vergelijk Tailscale SSH met klassieke SSH

Tailscale SSH is niet hetzelfde als klassieke SSH naar TCP/22.

Voeg een SSH-policy toe als je Tailscale SSH in deze workshop gebruikt:

```json
"ssh": [
  {
    "action": "accept",
    "src": ["autogroup:member"],
    "dst": ["tag:student-vm"],
    "users": ["debian"]
  }
]
```

Test Tailscale SSH:

```text
tailscale ssh debian@<vm1-name>
```

Test klassieke SSH:

```text
ssh debian@<vm1-tailscale-ip>
```

Vul in:

| Test | Verwacht | Werkelijk | Verklaring |
|---|---|---|---|
| `tailscale ssh debian@<vm1-name>` | werkt indien SSH-policy actief is | ... | ... |
| `ssh debian@<vm1-tailscale-ip>` | faalt als TCP/22 niet in ACL staat | ... | ... |
| `nc -vz <vm1-tailscale-ip> 22` | faalt als TCP/22 niet openstaat | ... | ... |

Controlepunt:

> Kan je uitleggen waarom Tailscale SSH kan werken terwijl klassieke SSH naar poort 22 faalt?

---

## 13. Stap 7: configureer VM2 als subnet router

VM2 krijgt nu een andere rol dan VM1.

VM2 wordt subnet router voor:

```text
10.20.0.0/16
```

Controleer op VM2 welk DHCP-IP het toestel kreeg:

```text
ip -br address
```

Zet IP forwarding aan op VM2:

```text
sudo sysctl -w net.ipv4.ip_forward=1
```

Meld VM2 aan of herstart Tailscale met de subnet route:

```text
sudo tailscale up --advertise-routes=10.20.0.0/16 --hostname=<VM2-NAME>
```

Keur daarna in je Tailscale admin console de route `10.20.0.0/16` goed.

Controleer op je laptop:

```text
tailscale status
```

Vul in:

| Controle | Verwacht | Werkelijk |
|---|---|---|
| VM2 zichtbaar in Tailscale | ja | ... |
| VM2 DHCP-IP genoteerd | ja | ... |
| VM2 adverteert route `10.20.0.0/16` | ja | ... |
| route goedgekeurd | ja | ... |
| VM2 herkenbaar als subnet router | ja | ... |

Beantwoord:

- Waarom is route adverteren niet hetzelfde als route mogen gebruiken?
- Waarom is `tag:subnet-router` een gevoelige tag?

Controlepunt:

> VM2 biedt nu technisch een pad naar het interne labnet, maar policy bepaalt nog altijd welke toegang bruikbaar is.

---

## 14. Stap 8: laat alleen HTTPS naar NetBox toe

NetBox staat vast op:

```text
10.20.10.4
```

Je krijgt geen SSH- of beheertoegang tot deze VM.

Voeg routed access toe voor alleen HTTPS naar NetBox.

Voorbeeld:

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "dst": ["10.20.10.4:443"]
}
```

Test op je laptop:

```text
curl -kI https://10.20.10.4
```

Vul in:

| Test | Verwacht | Werkelijk |
|---|---|---|
| HTTPS naar `10.20.10.4` | werkt | ... |
| Pad loopt via VM2 | ja | ... |

Beantwoord:

- Waarom gebruik je hier geen `tag:webserver:80`?
- Waarom is `10.20.10.4:443` preciezer dan `10.20.0.0/16:*`?
- Waarom krijg je geen shelltoegang tot NetBox?

Controlepunt:

> Je bereikt een bestaande interne HTTPS-dienst via routed subnet access, niet via Tailscale op NetBox zelf.

---

## 15. Stap 9: bewijs dat beheerpoorten niet bereikbaar zijn

Test nu bewust poorten die niet nodig zijn.

```text
nc -vz 10.20.10.4 22
nc -vz 10.20.10.4 80
nc -vz 10.20.0.1 22
```

Vul in:

| Test | Verwacht | Werkelijk | Conclusie |
|---|---|---|---|
| HTTPS naar `10.20.10.4:443` | werkt | ... | ... |
| SSH naar `10.20.10.4:22` | faalt | ... | ... |
| TCP/80 naar `10.20.10.4` | faalt tenzij bewust toegestaan | ... | ... |
| SSH naar DNS-server `10.20.0.1:22` | faalt | ... | ... |

Beantwoord:

- Wat bewijst de test naar `10.20.10.4:22`?
- Waarom mag de DNS-server zelf niet automatisch een breed beheerdoel worden?
- Wat zou er veranderen als je `10.20.0.0/16:*` toeliet?

Controlepunt:

> Een subnet route is pas least privilege wanneer ook onnodige poorten dicht blijven.

---

## 16. Stap 10: analyseer een brede routed ACL

Bekijk deze regel:

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "dst": ["10.20.0.0/16:*"]
}
```

Beantwoord:

- Welke hosts vallen binnen `10.20.0.0/16`?
- Welke poorten zijn toegestaan?
- Zou SSH naar `10.20.10.4` dan nog falen?
- Zou SSH naar `10.20.0.1` dan nog falen?
- Waarom is dit te breed voor de opdracht?

Schrijf een betere regel:

```json
...
```

Controlepunt:

> De juiste oplossing geeft toegang tot de dienst, niet tot het volledige labnet.

---

## 17. Stap 11: test Split DNS

Nu vervang je het IP-adres door een interne naam.

De lokale DNS-server is:

```text
10.20.0.1
```

Het interne record bestaat al:

```text
netbox.voltlab.lan -> 10.20.10.4
```

Zorg dat DNS-verkeer naar `10.20.0.1` mag.

Voorbeeld:

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "proto": "udp",
  "dst": ["10.20.0.1:53"]
}
```

Afhankelijk van DNS-clientgedrag kan TCP/53 ook nodig zijn.

Configureer in Tailscale DNS een restricted nameserver voor:

```text
voltlab.lan -> 10.20.0.1
```

Test:

```text
nslookup netbox.voltlab.lan
curl -kI https://netbox.voltlab.lan
```

Vul in:

| Test | Verwacht | Werkelijk |
|---|---|---|
| DNS-resolutie `netbox.voltlab.lan` | `10.20.10.4` | ... |
| HTTPS via hostname | werkt | ... |
| publieke DNS blijft werken | ja | ... |

Beantwoord:

- Waarom testte je eerst `curl -kI https://10.20.10.4`?
- Wat doet Split DNS?
- Wat is het verschil met MagicDNS?

Controlepunt:

> Split DNS maakt de interne dienst bruikbaar via naam, maar vervangt geen route of ACL.

---

## 18. Stap 12: open NetBox in de browser

Open in je browser:

```text
https://netbox.voltlab.lan
```

Je mag de HTTPS-pagina's bekijken.

Je logt niet in met beheerrechten.

Je voert geen scans of wijzigingen uit op NetBox.

Vul in:

| Controle | Verwacht | Werkelijk |
|---|---|---|
| NetBox-pagina opent via hostname | ja | ... |
| URL gebruikt `netbox.voltlab.lan` | ja | ... |
| toegang gebeurt via HTTPS | ja | ... |

Controlepunt:

> Je gebruikt NetBox als testdienst voor routed access en Split DNS, niet als server die je beheert.

---

## 19. Stap 13: audit en cleanup

Controleer je tailnet en policy.

Vul in:

| Controle | Verwacht | Werkelijk |
|---|---|---|
| Laptop herkenbaar | ja | ... |
| VM1 herkenbaar en correct getagd | ja | ... |
| VM2 herkenbaar als subnet router | ja | ... |
| VM2 route `10.20.0.0/16` bewust goedgekeurd | ja | ... |
| HTTPS naar `10.20.10.4` werkt | ja | ... |
| SSH naar `10.20.10.4` faalt | ja | ... |
| DNS voor `netbox.voltlab.lan` werkt | ja | ... |
| Geen permanente `*:*` regel | ja | ... |
| Geen brede `10.20.0.0/16:*` regel | ja | ... |
| Auth keys niet in verslag | ja | ... |
| Oude of fout aangemelde devices verwijderd | ja | ... |

Controlepunt:

> De workshop is pas klaar wanneer je kan aantonen dat nodige toegang werkt en onnodige toegang niet werkt.

---

## 20. In te dienen

Lever een kort technisch verslag in.

Je verslag bevat minstens:

1. device- en IP-plan voor laptop, VM1 en VM2;
2. baseline test van VM1 als Tailscale-device;
3. tag owners en gebruikte tags;
4. heraanmelding van VM1 met auth key, zonder secret;
5. ACL voor directe HTTP-toegang naar VM1;
6. negatieve tests naar TCP/22 en TCP/443 op VM1;
7. vergelijking tussen Tailscale SSH en klassieke SSH;
8. configuratie en goedkeuring van VM2 als subnet router;
9. ACL voor HTTPS naar `10.20.10.4:443`;
10. negatieve test naar `10.20.10.4:22`;
11. analyse van brede routed ACL `10.20.0.0/16:*`;
12. Split DNS-test voor `netbox.voltlab.lan`;
13. bewijs dat NetBox via HTTPS in de browser opent;
14. audit en cleanup;
15. eindconclusie.

Neem geen secrets op.

Geen auth keys.

Geen loginlinks.

Geen tokens.

Geen recovery codes.

---

## 21. Eindvraag

Sluit je verslag af met een antwoord op deze vraag:

> Waarom is "zelfde tailnet" geen voldoende securitybeleid, en waarom is een subnet route zonder beperkte ACL ook te breed?
