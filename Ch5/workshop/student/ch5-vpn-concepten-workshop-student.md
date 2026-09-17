# Workshop 5 - HTTP bereikbaar maken via Tailscale

## 1. Situering

In deze workshop krijg je een Debian VM met een eenvoudige webserver.

De VM staat achter een firewall op **Proxmox-niveau**.

Die firewall blokkeert inkomende HTTP-verzoeken naar de VM via het gewone netwerk.

Je kan die firewall niet aanpassen vanuit de VM.

Dat is bewust.

De opdracht is:

> Maak de webdienst bereikbaar via Tailscale, zonder de Proxmox-firewallregel te wijzigen.

Je leert dus niet hoe je een poort openzet.

Je leert hoe je een private overlay gebruikt om een interne dienst gecontroleerd bereikbaar te maken.

---

## 2. Scenario

**BluePeak Services** heeft interne Debian-servers met webinterfaces.

Die webinterfaces mogen niet zomaar bereikbaar zijn vanaf elk netwerk.

In de campusomgeving bestaan twee aparte draadloze netwerken:

| Netwerk | Rol in de workshop |
|---|---|
| Devbit | netwerk met rechtstreekse route naar de VM |
| eduroam | gescheiden netwerk zonder rechtstreekse toegang tot de VM |

Daarnaast blokkeert de Proxmox-firewall inkomende HTTP naar de VM.

Met Tailscale krijgt de VM een tweede, private toegang via de tailnet.

De centrale onderzoeksvraag is:

> Waarom werkt HTTP via Tailscale wel, terwijl rechtstreekse HTTP via het gewone netwerk niet werkt?

---

## 3. Beginsituatie

Je krijgt:

- een Debian VM per student;
- een lokale webserver op de VM;
- Proxmox-firewallregels die inkomende HTTP blokkeren;
- toegang tot Devbit en eduroam;
- een eigen Tailscale-account dat je zelf aanmaakt en gebruikt;
- de configbijlagen in `Ch5/workshop/configs/student/`.

Gebruik deze bijlagen:

| Bestand | Doel |
|---|---|
| `Ch5/workshop/configs/student/end-devices-student.md` | VM-, netwerk- en IP-plan |
| `Ch5/workshop/configs/student/tailscale-setup-student.md` | installatie- en controlecommands |
| `Ch5/workshop/configs/student/quick-tests-student.md` | korte testmatrix |

Veiligheidsregel:

> Noteer nooit wachtwoorden, auth keys, loginlinks, recovery codes of persoonlijke tokens in je verslag.

Accountregel:

> Je gebruikt je eigen Tailscale-account. Je VM en je testclient moeten in jouw persoonlijke tailnet zitten.

---

## 4. Doelen

Na deze workshop kan je:

1. het verschil uitleggen tussen Devbit, eduroam en Tailscale;
2. aantonen dat de webserver lokaal op de VM werkt;
3. aantonen dat HTTP via het gewone VM-IP geblokkeerd is;
4. Tailscale installeren op een Debian VM;
5. een eigen Tailscale-account en persoonlijke tailnet gebruiken;
6. het Tailscale-IP en de MagicDNS-naam bepalen;
7. HTTP via Tailscale-IP of MagicDNS testen;
8. uitleggen waarom de Proxmox-firewall niet hetzelfde ziet als HTTP via `tailscale0`;
9. positieve en negatieve tests documenteren;
10. uitleggen waarom dit veiliger is dan HTTP publiek openzetten;
11. een exit node gebruiken om full tunnel te demonstreren.

---

## 5. Benodigdheden

Je hebt nodig:

- Debian VM;
- sudo-rechten op de VM;
- internettoegang vanaf de VM;
- browser of `curl` op een testclient;
- toegang tot Devbit en eduroam;
- eigen Tailscale-account;
- terminal.

De VM bevat bij voorkeur al:

- `nginx` of `apache2`;
- `curl`;
- `iproute2`;
- `sudo`.

Studenten beheren de Proxmox-firewall niet.

---

## 6. Werkwijze

Gebruik deze volgorde:

1. VM en netwerkgegevens inventariseren;
2. lokale webserver controleren;
3. directe HTTP-test vanaf Devbit uitvoeren;
4. directe HTTP-test vanaf eduroam uitvoeren;
5. Tailscale-account aanmaken indien nodig;
6. Tailscale installeren en aanmelden op VM en testclient;
7. Tailscale-status controleren;
8. HTTP via Tailscale testen;
9. vergelijken waarom de paden verschillend zijn;
10. de verplichte challenges uitvoeren;
11. exit-node-demo uitvoeren;
12. verslag en reflectie schrijven.

---

## 7. Stap 1: inventariseer je VM

Voer op je Debian VM uit:

```text
hostname
ip -br addr
ip route
```

Vul in:

| Item | Waarde |
|---|---|
| Hostname | ... |
| VM-netwerkinterface | ... |
| VM-IP op gewoon netwerk | ... |
| Default gateway | ... |
| Tailscale-interface | nog niet aanwezig / `tailscale0` |
| Tailscale-IP | nog niet aanwezig / ... |
| Webserver | nginx/apache/andere |
| Firewalllocatie | Proxmox |

Controlepunt:

> Je kent het gewone VM-IP voordat je Tailscale installeert.

---

## 8. Stap 2: controleer de webserver lokaal

Test op de VM zelf:

```text
curl -I http://127.0.0.1
curl http://127.0.0.1
```

Verwacht:

- de webserver antwoordt lokaal;
- je ziet een HTTP-status zoals `200 OK`;
- de webpagina bevat herkenbare informatie over jouw VM.

Als de webserver niet draait:

```text
systemctl status nginx
```

of:

```text
systemctl status apache2
```

Controlepunt:

> De applicatie werkt lokaal. Als HTTP van buitenaf niet werkt, ligt het probleem dus bij netwerkpad, firewall of policy.

---

## 9. Stap 3: test rechtstreeks vanaf Devbit

Verbind je testclient met **Devbit**.

Controleer je client-IP.

Test daarna:

```text
curl -I http://<VM-IP>
```

Verwacht:

- het netwerkpad naar de VM bestaat;
- maar HTTP faalt door de Proxmox-firewall.

Vul in:

| Test | Bronnetwerk | Doel | Verwacht | Werkelijk |
|---|---|---|---|---|
| Direct HTTP | Devbit | `http://<VM-IP>` | faalt | ... |

Controlepunt:

> Devbit heeft rechtstreekse toegang tot de VM, maar dat betekent niet dat elke poort open is.

---

## 10. Stap 4: test rechtstreeks vanaf eduroam

Verbind je testclient met **eduroam**.

Controleer opnieuw je client-IP.

Test:

```text
curl -I http://<VM-IP>
```

Verwacht:

- de test faalt;
- eduroam zit in een ander netwerk;
- de VM is niet rechtstreeks bereikbaar zoals vanaf Devbit.

Vul in:

| Test | Bronnetwerk | Doel | Verwacht | Werkelijk |
|---|---|---|---|---|
| Direct HTTP | eduroam | `http://<VM-IP>` | faalt | ... |

Controlepunt:

> eduroam en Devbit zijn aparte netwerken. Directe bereikbaarheid is dus niet hetzelfde.

---

## 11. Stap 5: maak of gebruik je eigen Tailscale-account

Maak een eigen Tailscale-account aan of meld aan met je bestaande account.

Gebruik bij voorkeur je schoolaccount als de docent dat vraagt.

Je hebt minstens twee devices nodig in dezelfde persoonlijke tailnet:

| Device | Functie |
|---|---|
| Debian VM | webserver die je wil bereiken |
| Laptop/testclient | toestel waarmee je vanaf Devbit/eduroam test |

Controlepunt:

> Je testclient en je VM moeten in dezelfde tailnet zitten. Anders kan je jouw VM niet via het Tailscale-IP bereiken.

---

## 12. Stap 6: installeer Tailscale op de VM

Gebruik de installatiestappen uit de configbijlage of de instructies van de docent.

Voor Debian kan dit bijvoorbeeld:

```text
curl -fsSL https://tailscale.com/install.sh | sh
```

Meld de VM daarna aan:

```text
sudo tailscale up
```

Volg de loginflow.

Neem geen loginlinks of tokens op in je verslag.

Controleer:

```text
tailscale status
tailscale ip -4
ip -br addr show tailscale0
```

Vul aan:

| Item | Waarde |
|---|---|
| Tailscale device name | ... |
| Tailscale IPv4 | `100.x.x.x` |
| MagicDNS-naam | ... |
| Tailnet peers zichtbaar? | ja/nee |

---

## 13. Stap 7: installeer Tailscale op je testclient

Installeer Tailscale ook op je laptop of testclient.

Meld aan met hetzelfde Tailscale-account als op de VM.

Controleer op je testclient:

```text
tailscale status
tailscale ip -4
```

Je moet je Debian VM als peer zien.

Controlepunt:

> Als je VM en testclient niet allebei in je persoonlijke tailnet zitten, zal HTTP via Tailscale niet werken.

---

## 14. Stap 8: test Tailscale-connectiviteit

Test vanaf een andere tailnet-client naar jouw VM:

```text
tailscale ping <jouw-vm-name>
```

of:

```text
ping <jouw-tailscale-ip>
```

Controlepunt:

> Eerst bewijs je dat de VPN-overlay werkt. Pas daarna test je HTTP.

---

## 15. Stap 9: test HTTP via Tailscale

Verbind je testclient bij voorkeur met **eduroam**.

Test dan:

```text
curl -I http://<jouw-tailscale-ip>
```

Test daarna met MagicDNS:

```text
curl -I http://<jouw-magicdns-naam>
```

Vul in:

| Test | Bronnetwerk | Doel | Verwacht | Werkelijk |
|---|---|---|---|---|
| HTTP via Tailscale-IP | eduroam + Tailscale | `http://100.x.x.x` | werkt | ... |
| HTTP via MagicDNS | eduroam + Tailscale | `http://vm-naam` | werkt | ... |

Controlepunt:

> Je bereikt de webdienst vanaf eduroam via Tailscale, terwijl directe HTTP naar het VM-IP faalt.

---

## 16. Stap 10: vergelijk de drie paden

Vul de tabel in.

| Pad | Voorbeeld | Verwacht | Waarom? |
|---|---|---|---|
| Devbit direct naar VM-IP | `http://<VM-IP>` | faalt | Proxmox-firewall blokkeert HTTP |
| eduroam direct naar VM-IP | `http://<VM-IP>` | faalt | ander netwerk en/of firewall |
| eduroam + Tailscale naar Tailscale-IP | `http://100.x.x.x` | werkt | verkeer loopt via tailnet |

Maak daarna een klein schema:

```text
Devbit client  --X-->  VM-IP:80

eduroam client --X-->  VM-IP:80

eduroam client + Tailscale  -->  Tailscale-IP:80
```

Beantwoord:

- Welk pad gebruikt het gewone VM-IP?
- Welk pad gebruikt het Tailscale-IP?
- Waar wordt HTTP geblokkeerd?
- Waarom kan de student die blokkering niet uitzetten?
- Waarom is Tailscale hier geen gewone port-forward?

---

## 17. Challenge 1: MagicDNS

Gebruik de MagicDNS-naam van je VM in plaats van het Tailscale-IP.

Test:

```text
curl -I http://<magicdns-naam>
```

Beantwoord:

- Waarom is een naam beheerbaarder dan een `100.x.x.x`-adres?
- Wat controleer je als IP werkt maar MagicDNS niet?

---

## 18. Challenge 2: devicebeheer

Open de Tailscale admin console van je eigen account.

Zoek je VM en je testclient.

Vul in:

| Vraag | Antwoord |
|---|---|
| Hoe heet je VM in Tailscale? | ... |
| Hoe heet je testclient? | ... |
| Wanneer was de VM laatst online? | ... |
| Welk OS wordt getoond? | ... |
| Is de naam duidelijk genoeg? | ja/nee |

Voer minstens een van deze acties uit als de docent dit toestaat:

- geef je VM een herkenbare naam;
- controleer of MagicDNS die naam gebruikt;
- verwijder een oud of fout device uit je tailnet;
- noteer welke devices je na de workshop moet opruimen.

Controlepunt:

> Een tailnet is ook een inventaris. Onbekende devices zijn een securityrisico.

---

## 19. Challenge 3: exit node via Devbit

In deze variant gebruik je een Tailscale exit node op Devbit.

Dat kan op twee manieren:

- je eigen Debian VM adverteert zichzelf als exit node in jouw persoonlijke tailnet;
- de docent demonstreert een exit node in een aparte demo-tailnet.

Daarmee kan je tonen wat full tunnel betekent.

Test zonder exit node:

```text
curl https://ifconfig.me
```

Activeer daarna de exit node via de Tailscale client of volgens instructie van de docent.

Test opnieuw:

```text
curl https://ifconfig.me
```

Vul in:

| Situatie | Verbonden met wifi | Exit node | Publiek IP |
|---|---|---|---|
| Zonder exit node | eduroam | nee | ... |
| Met Devbit exit node | eduroam | ja | ... |

Controlepunt:

> Je bent fysiek verbonden met eduroam, maar je internetverkeer gaat via een exit node op Devbit naar buiten.

Reflectie:

- Waarom hoort dit bij full tunnel?
- Welke privacy- en loggingvragen ontstaan?
- Is dit nodig voor de HTTP-toegang tot je VM?

---

## 20. Risicoanalyse

Beschrijf minstens vijf risico's.

| Risico | Impact | Maatregel |
|---|---|---|
| Elk device in jouw tailnet mag HTTP | te brede toegang | devices beperken en opruimen |
| Verloren of gedeelde login | onbevoegde toegang | device verwijderen, MFA |
| Onveilige webapp | VPN beschermt transport maar niet app | app-authenticatie en updates |
| MagicDNS verwarring | verkeerde host getest | device-inventaris |
| Oude VM blijft in tailnet | vergeten toegang | cleanup na workshop |
| Exit node verkeerd gebruikt | al het internetverkeer loopt via Devbit | duidelijke policy en logging |

Controlepunt:

> Tailscale lost het bereikbaarheidsprobleem op, maar vervangt geen applicatiebeveiliging.

---

## 21. In te dienen

Lever een kort technisch verslag in.

Je verslag bevat minstens:

1. VM-inventaris met VM-IP, Tailscale-IP en hostname;
2. bewijs dat de webserver lokaal werkt;
3. bewijs dat HTTP direct via Devbit faalt;
4. bewijs dat HTTP direct via eduroam faalt;
5. Tailscale-status en Tailscale-IP;
6. bewijs dat HTTP via Tailscale werkt;
7. MagicDNS-test;
8. vergelijking van Devbit, eduroam en Tailscale;
9. device-inventaris in je persoonlijke tailnet;
10. uitgevoerde challenges;
11. risicoanalyse;
12. eindconclusie.

Neem geen secrets op.

Geen wachtwoorden.

Geen auth keys.

Geen persoonlijke tokens.

Geen recovery codes.

---

## 22. Eindvraag

Sluit je verslag af met een antwoord op deze vraag:

> Waarom is HTTP via Tailscale bereikbaar maken iets anders dan HTTP op de VM publiek openzetten?
