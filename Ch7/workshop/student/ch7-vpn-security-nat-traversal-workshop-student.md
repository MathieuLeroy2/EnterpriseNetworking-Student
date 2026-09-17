# Workshop 7 - VPN security en NAT traversal onderzoeken met Tailscale

## 1. Situering

In deze workshop gebruik je een Debian-VM in het Devbit-netwerk als server.

Je laptop is de client. Je test vanaf twee verschillende fysieke netwerken:

- Devbit;
- eduroam of campusroam.

De Debian-server blijft tijdens alle testen in Devbit staan. Alleen je laptop wisselt van netwerk.

Je configureert niets op routers, switches, access points of de Proxmox-firewall. Je onderzoekt hoe Tailscale ondanks NAT en stateful firewalls een beveiligd pad probeert op te bouwen.

De centrale onderzoeksvraag is:

> Hoe blijft dezelfde Debian-server veilig bereikbaar wanneer de client van netwerk verandert, welk datapad gebruikt Tailscale en welke informatie blijft onderweg zichtbaar?

Belangrijk:

> Een directe verbinding en een DERP-verbinding zijn allebei geldige labresultaten. Je wordt beoordeeld op correcte metingen en interpretatie, niet op het afdwingen van een bepaald pad.

---

## 2. Scenario

**BluePeak Services** beheert een Debian-server in een afgeschermd campusnetwerk.

Een beheerder wil de server vanaf een laptop bereiken:

- eerst vanuit Devbit;
- daarna vanuit eduroam of campusroam;
- zonder een publieke applicatiepoort;
- zonder port forwarding;
- zonder wijzigingen aan de campusinfrastructuur.

De beheerder moet aan het securityteam kunnen uitleggen:

1. waarom de verbinding over een onbekend netwerk toch beschermd is;
2. of het datapad direct, via een peer relay of via DERP loopt;
3. welke rol NAT, PAT en stateful firewalls spelen;
4. wat de netwerkbeheerder, Tailscale-beheerder en relaybeheerder kunnen zien;
5. waarom werkende VPN-connectiviteit niet automatisch volledige autorisatie of applicatiebeveiliging betekent.

---

## 3. Topologie en grenzen van het labo

```text
                         Tailscale control plane
                    login, keys, endpoints en policy
                                   |
                                   |
Laptop                        internet/campus                    Debian-VM
Tailscale-client  ===== versleutelde data plane =====>  Tailscale-server
     |                                                           |
     +-- test A: Devbit                             altijd in Devbit
     |
     +-- test B: eduroam/campusroam
```

Mogelijke datapaden:

```text
direct:
laptop == versleutelde UDP-verbinding == Debian-server

DERP:
laptop == versleuteld == DERP-relay == versleuteld == Debian-server

peer relay, alleen als de tailnet er een heeft:
laptop == versleuteld == tailnet-peer-relay == versleuteld == Debian-server
```

Niet toegestaan in deze workshop:

- router- of switchconfiguratie wijzigen;
- UPnP, NAT-PMP of PCP activeren;
- port forwarding instellen;
- campusfirewallregels wijzigen;
- UDP blokkeren om kunstmatig relaygebruik af te dwingen;
- captures maken van verkeer van andere studenten.

---

## 4. Beginsituatie

Je beschikt over:

| Component | Rol | Netwerk |
|---|---|---|
| Debian-VM | vaste server | Devbit |
| Laptop | Tailscale-client en meettoestel | eerst Devbit, daarna eduroam/campusroam |
| Persoonlijke tailnet | identity, keys, endpointinformatie en policy | Tailscale control plane |

Je Debian-VM heeft:

- een Devbit-IP via DHCP of de voorziene labconfiguratie;
- internettoegang voor package-installatie en Tailscale-login;
- `sudo`-rechten;
- geen vereiste publieke inbound poort.

Gebruik je VM uit een vorige workshop, controleer dan eerst de huidige Tailscale-status en policy. Oude tags, routes of ACLs kunnen je resultaten beïnvloeden.

---

## 5. Doelen

Na deze workshop kan je:

1. Tailscale op een Debian-server installeren en veilig aanmelden;
2. een serverdienst alleen op het Tailscale-adres laten luisteren;
3. control plane en data plane in de gemeten omgeving onderscheiden;
4. `tailscale status`, `tailscale ping` en `tailscale netcheck` gebruiken;
5. endpoint discovery en NAT mapping uit `netcheck` afleiden;
6. direct, peer relay en DERP in output herkennen;
7. verklaren waarom een verbinding eerst relayed en daarna direct kan zijn;
8. hetzelfde Tailscale-pad vanaf twee fysieke netwerken vergelijken;
9. latency en throughput voorzichtig vergelijken;
10. versleutelde buitentunnel en ontsleuteld verkeer op `tailscale0` onderscheiden;
11. aantonen dat Tailscale standaard split tunnel gebruikt;
12. zichtbare metadata onderscheiden van afgeschermde inhoud;
13. positieve en negatieve securitytests uitvoeren;
14. een minimale firewall- of port-forwardingbeslissing formuleren zonder ze uit te voeren;
15. typische VPN-misverstanden weerleggen.

---

## 6. Benodigdheden

Op de Debian-VM:

- terminaltoegang;
- `curl`;
- Python 3;
- `tcpdump`;
- `iperf3`;
- Tailscale.

Op de laptop:

- Tailscale-client;
- terminal of PowerShell;
- `curl.exe` of `curl`;
- `iperf3` indien beschikbaar;
- toegang tot Devbit en eduroam/campusroam.

Als `iperf3` niet op de laptop kan worden geïnstalleerd, voer je de HTTP-, ping- en padmetingen wel uit en noteer je throughput als `niet gemeten`.

---

## 7. Meetdiscipline en privacy

Bewaar van elke test:

- datum en tijd;
- fysiek netwerk van de laptop;
- lokaal laptop-IP;
- Tailscale-IP van laptop en server;
- relevante `netcheck`-velden;
- connection type;
- latency;
- throughput indien gemeten;
- je interpretatie.

Publiceer in je verslag niet onnodig:

- login-URL's;
- auth keys;
- publieke IP-adressen;
- volledige MagicDNS-namen als daar persoonsgegevens in staan;
- device keys;
- captures van verkeer van anderen.

Redacteer publieke adressen bijvoorbeeld als:

```text
193.***.***.42:51234
```

---

## 8. Stap 1: inventariseer de Debian-server

Voer op de VM uit:

```text
hostnamectl
ip -br address
ip route
ip route get 1.1.1.1
```

Noteer:

| Eigenschap | Waarde |
|---|---|
| VM-hostname | ... |
| Devbit-interface | ... |
| Devbit-IPv4 | ... |
| Default gateway | ... |
| Tailscale al geïnstalleerd? | ja/nee |

Voorspel vóór je Tailscale gebruikt:

| Test vanaf campusroam | Voorspelling | Waarom? |
|---|---|---|
| ping naar Devbit-IP | ... | ... |
| TCP/8080 naar Devbit-IP | ... | ... |
| Tailscale-IP zonder actieve Tailscale-client | ... | ... |

Controlepunt:

> Het Devbit-IP is een underlay-adres. Het toekomstige Tailscale-IP is een overlay-adres. Die adressen beschrijven niet hetzelfde pad.

---

## 9. Stap 2: installeer de meettools en Tailscale

Installeer eerst de labtools:

```text
sudo apt update
sudo apt install -y curl python3 tcpdump iperf3
```

Kies `No` als de installatie vraagt om `iperf3` permanent als systeemdaemon te starten. Je start de testserver later zelf.

Installeer Tailscale met de officiële installatiemethode:

```text
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Open de getoonde login-URL en meld de VM aan in je eigen tailnet.

Controleer:

```text
systemctl is-active tailscaled
tailscale version
tailscale status
tailscale ip -4
ip -br address show tailscale0
```

Noteer:

| Eigenschap | Waarde |
|---|---|
| Tailscale-versie | ... |
| VM Tailscale-IPv4 | ... |
| VM MagicDNS-naam | ... |
| `tailscale0` aanwezig | ja/nee |
| VM zichtbaar in admin console | ja/nee |

Securityvraag:

> Welke geheime sleutel moet op de VM blijven en waarom mag je een login-URL of auth key niet in je verslag opnemen?

---

## 10. Stap 3: meld de laptop aan

Installeer of open Tailscale op de laptop en meld aan in dezelfde persoonlijke tailnet als de VM.

Controleer op de laptop:

```text
tailscale status
tailscale ip -4
```

Als `tailscale` op Windows niet in `PATH` staat, gebruik je de Tailscale-terminaloptie of het volledige pad dat de docent aangeeft.

Noteer:

| Eigenschap | Waarde |
|---|---|
| Laptop device name | ... |
| Laptop Tailscale-IPv4 | ... |
| Server zichtbaar als peer | ja/nee |
| Zelfde tailnet | ja/nee |

Leg uit:

- wat de control plane tijdens het aanmelden deed;
- waarom de control plane niet automatisch het latere HTTP-dataverkeer hoeft te vervoeren;
- welke rol public en private keys spelen.

---

## 11. Stap 4: start een serverdienst op het overlay-adres

De webdienst luistert bewust alleen op het Tailscale-IP. Zo wordt ze niet per ongeluk op het Devbit-IP gepubliceerd.

Voer op de VM uit:

```text
mkdir -p "$HOME/ch7-vpn-lab"
echo "CH7 VPN LAB - $(hostname)" > "$HOME/ch7-vpn-lab/index.html"
CH7_TS_IP="$(tailscale ip -4)"
test -n "$CH7_TS_IP" || { echo "Geen Tailscale IPv4 gevonden"; exit 1; }
nohup python3 -m http.server 8080 --bind "$CH7_TS_IP" --directory "$HOME/ch7-vpn-lab" > "$HOME/ch7-http.log" 2>&1 &
echo $! > "$HOME/ch7-http.pid"
```

Controleer op de VM:

```text
ss -lntp | grep ':8080'
curl "http://$(tailscale ip -4):8080"
```

Verwacht:

- TCP/8080 luistert op het Tailscale-IP;
- de testpagina bevat je VM-hostname;
- TCP/8080 luistert niet op `0.0.0.0` en niet op het Devbit-IP.

Vul in:

| Controle | Verwacht | Werkelijk |
|---|---|---|
| lokaal via Tailscale-IP | werkt | ... |
| listener op `100.x.x.x:8080` | ja | ... |
| listener op `0.0.0.0:8080` | nee | ... |

Kernzin:

> De VPN maakt een pad naar de server, maar de servicebinding bepaalt op welke interface de applicatie werkelijk luistert.

---

## 12. Stap 5: maak een baseline vanuit Devbit

Verbind de laptop met Devbit. Noteer het lokale laptop-IP en controleer dat de VM nog in Devbit staat.

Voer op de laptop uit:

```text
tailscale netcheck
tailscale ping --c 10 --until-direct=false <VM-NAME-OF-TAILSCALE-IP>
tailscale status
```

Test daarna de applicatie:

```text
curl.exe http://<VM-TAILSCALE-IP>:8080
```

Gebruik op Linux of macOS `curl` in plaats van `curl.exe`.

Voer ook de negatieve directe test uit:

```text
curl.exe --connect-timeout 5 http://<VM-DEVBIT-IP>:8080
```

Vul de Devbit-meting in:

| Meetpunt | Resultaat |
|---|---|
| `UDP` | true/false |
| `IPv4` | aanwezig/afwezig, adres geredacteerd |
| `IPv6` | aanwezig/afwezig |
| `MappingVariesByDestIP` | true/false/leeg |
| `PortMapping` | ... |
| `Nearest DERP` | ... |
| eerste pingpad | direct/DERP/peer relay |
| stabiel pingpad | direct/DERP/peer relay |
| pinglatency | ... ms |
| HTTP via Tailscale-IP | werkt/faalt |
| HTTP via Devbit-IP | werkt/faalt |

Let op:

> Een eerste pong via DERP en een latere pong via een publiek of lokaal endpoint is geen fout. Tailscale gebruikt de relay voor connectieopbouw en probeert daarna naar direct UDP te upgraden.

---

## 13. Stap 6: interpreteer `tailscale netcheck`

Gebruik je eigen Devbit-output en vul in:

| Veld | Wat meet het? | Wat betekent jouw waarde? |
|---|---|---|
| `UDP` | kan een STUN-server outbound UDP ontvangen? | ... |
| `IPv4` | welk publiek endpoint wordt waargenomen? | ... |
| `IPv6` | is bruikbare IPv6-connectiviteit aanwezig? | ... |
| `MappingVariesByDestIP` | blijft de mapping gelijk voor verschillende bestemmingen? | ... |
| `PortMapping` | werden UPnP, NAT-PMP of PCP ontdekt? | ... |
| `Nearest DERP` | welke relay heeft de laagste gemeten latency? | ... |

Beantwoord:

1. Is een publiek endpoint hetzelfde als het lokale IP van de laptop?
2. Welke component ontdekte het publieke endpoint?
3. Is endpoint discovery hetzelfde als applicatiedata relayeren?
4. Waarom kan `MappingVariesByDestIP: true` directe connectiviteit moeilijker maken?
5. Waarom bewijst `PortMapping` leeg niet dat er geen NAT of NAT mapping aanwezig is?
6. Wat is het verschil tussen een tijdelijke NAT mapping en een bewust ingestelde port mapping?

---

## 14. Stap 7: meet throughput vanuit Devbit

Start op de VM een tijdelijke `iperf3`-server die alleen op het Tailscale-IP luistert:

```text
CH7_TS_IP="$(tailscale ip -4)"
test -n "$CH7_TS_IP" || { echo "Geen Tailscale IPv4 gevonden"; exit 1; }
nohup iperf3 -s -B "$CH7_TS_IP" > "$HOME/ch7-iperf3.log" 2>&1 &
echo $! > "$HOME/ch7-iperf3.pid"
ss -lntp | grep ':5201'
```

Test op de laptop:

```text
iperf3 -c <VM-TAILSCALE-IP> -t 15
iperf3 -c <VM-TAILSCALE-IP> -t 15 -R
```

Vul in:

| Richting | Throughput | Retransmits of packet loss | Connection type tijdens test |
|---|---:|---:|---|
| laptop naar VM | ... | ... | ... |
| VM naar laptop (`-R`) | ... | ... | ... |

Voer vlak na de transfer opnieuw uit:

```text
tailscale status
```

Belangrijk:

> Eén korte throughputmeting bewijst niet dat een netwerk structureel sneller is. Noteer het pad, de richting en de omstandigheden.

---

## 15. Stap 8: wissel alleen de laptop naar eduroam of campusroam

Laat de Debian-VM in Devbit staan.

Verbreek op de laptop de Devbit-verbinding en verbind met eduroam of campusroam. Zorg dat niet beide fysieke netwerken tegelijk actief blijven.

Controleer:

- het lokale laptop-IP is veranderd;
- de default route is veranderd;
- het Tailscale-IP van de laptop is gelijk gebleven;
- de server is nog zichtbaar in `tailscale status`.

Op Windows kan je gebruiken:

```text
Get-NetIPConfiguration
Get-NetRoute -DestinationPrefix 0.0.0.0/0
tailscale ip -4
```

Op Linux:

```text
ip -br address
ip route
tailscale ip -4
```

Vul in:

| Eigenschap | Devbit | eduroam/campusroam |
|---|---|---|
| lokaal laptop-IP | ... | ... |
| default gateway | ... | ... |
| laptop Tailscale-IP | ... | ... |
| VM Tailscale-IP | ... | ... |

Leg uit waarom de overlayadressen stabiel kunnen blijven terwijl het underlay-netwerk verandert.

---

## 16. Stap 9: herhaal de NAT- en padmetingen

Voer op de laptop via eduroam/campusroam uit:

```text
tailscale netcheck
tailscale ping --c 10 --until-direct=false <VM-NAME-OF-TAILSCALE-IP>
tailscale status
curl.exe http://<VM-TAILSCALE-IP>:8080
curl.exe --connect-timeout 5 http://<VM-DEVBIT-IP>:8080
```

Herhaal indien mogelijk ook:

```text
iperf3 -c <VM-TAILSCALE-IP> -t 15
iperf3 -c <VM-TAILSCALE-IP> -t 15 -R
```

Vul de tweede meting in:

| Meetpunt | Resultaat |
|---|---|
| `UDP` | true/false |
| publiek endpoint | geredigeerd |
| `MappingVariesByDestIP` | true/false/leeg |
| `PortMapping` | ... |
| `Nearest DERP` | ... |
| eerste pingpad | direct/DERP/peer relay |
| stabiel pingpad | direct/DERP/peer relay |
| pinglatency | ... ms |
| HTTP via Tailscale-IP | werkt/faalt |
| HTTP via Devbit-IP | werkt/faalt |
| throughput heen | ... |
| throughput terug | ... |

Kies de conclusie die bij je meting past en werk ze uit:

- beide netwerken leveren een directe verbinding;
- Devbit is direct en campusroam is relayed;
- beide verbindingen blijven relayed;
- het pad verandert tijdens de meting;
- de verbinding faalt en moet methodisch onderzocht worden.

Je mag niet concluderen dat NAT traversal mislukt alleen omdat het publieke IP veranderde. Een netwerkverandering hoort juist een nieuw endpoint en mogelijk een nieuwe NAT mapping op te leveren.

---

## 17. Stap 10: vergelijk direct en relay correct

Vul op basis van cursus en metingen in:

| Eigenschap | Direct | Peer relay | DERP relay |
|---|---|---|---|
| datapad | ... | ... | ... |
| end-to-end WireGuard-encryptie | ... | ... | ... |
| extra tussenpunt | ... | ... | ... |
| verwachte latency | ... | ... | ... |
| verwachte throughput | ... | ... | ... |
| metadata bij relay | ... | ... | ... |

Beantwoord:

1. Is relaygebruik automatisch onveilig?
2. Waarom is direct meestal sneller?
3. Waarom kan een directe verbinding beleidsmatig toch ongewenst zijn?
4. Waarom kan je uit één latencywaarde niet bewijzen dat DERP de enige bottleneck is?
5. Welke rol spelen packet loss, jitter, CPU en MTU naast het connection type?

---

## 18. Stap 11: observeer de encryptiegrens

Je maakt alleen een capture van verkeer naar je eigen VM.

### 18.1 Binnenkant van de tunnel

Start op de VM:

```text
sudo tcpdump -ni tailscale0 -s 0 -A 'tcp port 8080'
```

Stuur vanaf de laptop een herkenbare marker:

```text
curl.exe -H "X-Ch7-Marker: eigen-voornaam" http://<VM-TAILSCALE-IP>:8080
```

Stop de capture met `Ctrl+C`.

Noteer:

- is TCP/8080 zichtbaar;
- is de HTTP-request zichtbaar;
- is je marker zichtbaar;
- waarom is dit verkeer op `tailscale0` al ontsleuteld?

### 18.2 Buitenkant van de tunnel

Bepaal eerst op de VM de Devbit-interface en activeer het pad naar de laptop:

```text
ip route show default
tailscale ping --c 3 --until-direct=false <LAPTOP-NAME-OF-TAILSCALE-IP>
tailscale status
```

Lees in de regel van je eigen laptop of het actuele pad `direct`, `relay` of `peer-relay` is. Gebruik daarna alleen het bijbehorende filter. Combineer UDP/41641 en alle TCP/443 niet in één brede capture.

#### Direct pad

Bij een direct pad toont `tailscale status` bijvoorbeeld:

```text
active; direct 193.***.***.42:51234
```

Noteer:

- het IP-gedeelte als `<PEER-ENDPOINT-IP>`;
- de poort achter de dubbele punt als `<PEER-ENDPOINT-POORT>`;
- de lokale Tailscale-UDP-poort uit:

```text
sudo ss -lunp | grep tailscaled
```

De lokale poort is standaard vaak `41641`, maar de werkelijke `ss`-output is bepalend.

Start in een tweede VM-terminal een korte capture. Dit filter neemt alleen UDP tussen de VM en het actuele endpoint van jouw laptop mee:

```text
sudo timeout 10 tcpdump -ni <DEVBIT-INTERFACE> -s 0 -w /tmp/ch7-outer-direct.pcap 'udp and host <PEER-ENDPOINT-IP> and port <PEER-ENDPOINT-POORT> and port <LOKALE-TAILSCALE-UDP-POORT>'
```

Bij een direct IPv6-endpoint gebruik je het IPv6-adres zonder vierkante haken en voeg je `ip6 and` aan het begin van het filter toe.

#### DERP-relaypad

Bij `relay "<regiocode>"` loopt de datastroom over een bestaande `tailscaled`-verbinding naar TCP/443. `tcpdump` kan niet rechtstreeks op een procesnaam filteren. Zoek daarom eerst de actuele socket:

```text
sudo ss -ntpi | grep -A 1 tailscaled
```

Noteer bij de DERP-verbinding:

- het remote adres als `<DERP-IP>`;
- de lokale tijdelijke TCP-poort als `<LOKALE-DERP-TCP-POORT>`.

Voorbeeld van de relevante delen van een socket:

```text
<VM-DEVBIT-IP>:43852    <DERP-IP>:443
```

Hier is `43852` de lokale tijdelijke poort. Als je meerdere `tailscaled`-verbindingen naar TCP/443 ziet, vergelijk je `ss -ntpi` vóór en tijdens enkele HTTP-requests of een korte `iperf3`-transfer. Kies de socket waarvan de bytecounters toenemen. Raad niet op basis van alleen een willekeurig TCP/443-adres.

Capture daarna alleen die ene TCP-verbinding:

```text
sudo timeout 10 tcpdump -ni <DEVBIT-INTERFACE> -s 0 -w /tmp/ch7-outer-derp.pcap 'tcp and host <DERP-IP> and port 443 and port <LOKALE-DERP-TCP-POORT>'
```

Bij `peer-relay` pas je hetzelfde principe toe: neem het concrete peer-relayendpoint uit `tailscale status` en filter alleen op dat adres en die relaypoort.

#### Genereer en inspecteer de capture

Voer tijdens de capture vanaf de laptop dezelfde HTTP-request drie keer uit:

```text
curl.exe -H "X-Ch7-Marker: eigen-voornaam" http://<VM-TAILSCALE-IP>:8080
```

Wacht tot de capture na tien seconden stopt. Kies daarna het bestand dat bij jouw pad hoort:

```text
sudo tcpdump -nn -r /tmp/ch7-outer-direct.pcap
sudo tcpdump -A -nn -r /tmp/ch7-outer-direct.pcap | grep -F 'X-Ch7-Marker'
```

Gebruik bij DERP `/tmp/ch7-outer-derp.pcap`.

Verwacht:

- de eerste opdracht toont een kleine, gerichte set buitenste pakketten;
- de tweede opdracht vindt de leesbare HTTP-marker niet;
- geen grep-output is hier het verwachte resultaat.

Interpretatie:

- bij direct verkeer verwacht je meestal UDP voor de buitenste Tailscale-datastroom;
- bij DERP kan je een verbinding naar een relay via TCP/443 zien;
- poort `41641/udp` is de standaard luisterpoort, maar kan afwijken;
- de HTTP-marker hoort niet als leesbare applicatie-inhoud in de buitentunnel te verschijnen;
- een filter op alleen `tcp port 443` is te breed omdat het ook ander HTTPS-verkeer bevat;
- controleer na de capture opnieuw `tailscale status`, want het pad kan tijdens de meting van relay naar direct veranderen.

Vul in:

| Capturepunt | Zichtbaar | Niet leesbaar of niet aantoonbaar |
|---|---|---|
| `tailscale0` | ... | ... |
| fysieke Devbit-interface | ... | ... |

Kernzin:

> Op `tailscale0` bekijkt het endpoint het ontsleutelde inner packet. Op de fysieke interface ziet de netwerklaag de versleutelde buitentunnel en metadata.

---

## 19. Stap 12: toon split tunnel aan

Tailscale gebruikt zonder exit node standaard split tunnel: tailnetverkeer gaat via Tailscale, gewoon internetverkeer gebruikt de lokale default route.

Voer op de laptop uit terwijl Tailscale actief is:

```text
tailscale status
curl.exe https://ifconfig.me/ip
```

Controleer daarnaast de route naar de server en de gewone default route.

Op Windows:

```text
Find-NetRoute -RemoteIPAddress <VM-TAILSCALE-IP>
Get-NetRoute -DestinationPrefix 0.0.0.0/0
```

Op Linux:

```text
ip route get <VM-TAILSCALE-IP>
ip route get 1.1.1.1
```

### 19.1 Controleer MagicDNS apart

Test naast het Tailscale-IP ook de MagicDNS-naam of korte devicenaam:

```text
tailscale ping <VM-MAGICDNS-NAAM>
curl.exe http://<VM-MAGICDNS-NAAM>:8080
```

Controleer op Windows welke naam en resolver gebruikt worden:

```text
Resolve-DnsName <VM-MAGICDNS-NAAM>
Get-DnsClientServerAddress
```

Gebruik op Linux:

```text
getent ahostsv4 <VM-MAGICDNS-NAAM>
resolvectl status
```

Als MagicDNS in je tailnet niet actief is, noteer je dat als configuratie-uitkomst en gebruik je het Tailscale-IP voor de overige testen.

Beantwoord:

1. Lost de naam op naar het Tailscale-IP?
2. Welke informatie zou een gewone lokale DNS-query over interne namen kunnen lekken?
3. Waarom is werkende IP-connectiviteit geen bewijs dat DNS correct werkt?
4. Wat is het verschil tussen MagicDNS en Split DNS uit Ch6?

Beantwoord:

1. Gaat verkeer naar de VM via het Tailscale-pad?
2. Gaat algemeen internetverkeer via een geconfigureerde exit node?
3. Welke partij ziet gewone internetbestemmingen bij deze split-tunnelopzet?
4. Hoe zou de zichtbaarheid verschuiven bij full tunnel via een exit node?

Je configureert in deze workshop geen exit node.

---

## 20. Stap 13: voer negatieve securitytests uit

Koppel eerst de security-eigenschappen uit de cursus aan dit labo:

| Eigenschap | Wat levert Tailscale of WireGuard? | Wat moet policy, endpoint of applicatie nog leveren? |
|---|---|---|
| vertrouwelijkheid | ... | ... |
| integriteit | ... | ... |
| authenticatie | ... | ... |
| autorisatie | ... | ... |
| replaybescherming | ... | ... |
| forward secrecy | ... | ... |
| beschikbaarheid | ... | ... |

Voer de volgende tests uit vanaf eduroam/campusroam:

| Test | Verwacht | Werkelijk | Securitybetekenis |
|---|---|---|---|
| HTTP naar VM Tailscale-IP met Tailscale actief | werkt | ... | toegestaan overlaypad |
| HTTP naar VM Devbit-IP | faalt | ... | geen rechtstreeks campuspad en service luistert daar niet |
| HTTP naar VM Tailscale-IP op verkeerde poort `8081` | faalt | ... | VPN opent niet automatisch alle services |
| HTTP naar VM Tailscale-IP met Tailscale tijdelijk uit | faalt | ... | geen tailnetroute zonder client |

Schakel Tailscale op de laptop kort uit via de client en test alleen het Tailscale-IP. Schakel de client daarna onmiddellijk opnieuw in.

Als je een restrictieve ACL uit Ch6 gebruikt, controleer dan bovendien dat alleen de noodzakelijke labpoorten bereikbaar zijn. Maak geen brede `*:*`-regel om troubleshooting te omzeilen.

Beantwoord:

1. Bewijst werkende HTTP dat de applicatie zelf authenticatie heeft?
2. Welke bescherming levert de VPN wel?
3. Welke bescherming moet nog door ACL, host firewall of applicatie geleverd worden?
4. Waarom zijn encryptie en autorisatie verschillende eigenschappen?
5. Waarom kan de campusbeheerder pakketten droppen of vertragen, maar ze niet ongemerkt als geldige WireGuard-pakketten aanpassen?

---

## 21. Stap 14: maak een zichtbaarheidstabel

Vul voor jouw scenario in:

| Partij | Kan waarschijnlijk zien | Kan normaal niet zien |
|---|---|---|
| beheerder van eduroam/campusroam | ... | ... |
| Devbit-firewallbeheerder | ... | ... |
| ISP of upstream provider | ... | ... |
| Tailscale/tailnet-beheerder | ... | ... |
| DERP-beheerder, indien gebruikt | ... | ... |
| Debian-server zelf | ... | ... |

Verwerk minstens:

- lokaal en publiek IP;
- poorten en protocol;
- timing en volume;
- DNS of MagicDNS;
- users, devices, keys, tags en policy;
- HTTP-pad en header;
- de inhoud van de testpagina;
- connection type.

Nuanceer expliciet:

> Versleutelde inhoud is niet hetzelfde als onzichtbare metadata. Een VPN verschuift vertrouwen en zichtbaarheid; hij maakt de gebruiker niet automatisch anoniem.

---

## 22. Stap 15: koppel observaties aan control en data plane

Classificeer:

| Observatie | Control plane of data plane? | Waarom? |
|---|---|---|
| VM aanmelden in de tailnet | ... | ... |
| public keys en endpointinformatie verspreiden | ... | ... |
| ACL-policy ontvangen | ... | ... |
| `curl` naar TCP/8080 | ... | ... |
| `iperf3`-transfer | ... | ... |
| versleutelde pakketten via DERP | ... | ... |
| device verwijderen uit de admin console | ... | ... |

Beantwoord:

> Als `tailscale ping` een direct endpoint toont, welke partij transporteert dan de HTTP-payload tussen laptop en server?

---

## 23. Stap 16: ontwerp een netwerkbeslissing zonder ze uit te voeren

Stel dat de verbinding langdurig via DERP loopt en grote transfers te traag zijn.

Je mag de infrastructuur niet wijzigen. Schrijf daarom alleen een advies voor de netwerkbeheerder.

Vul in:

| Mogelijke maatregel | Verwachte winst | Securityrisico | Advies voor dit tijdelijke labo |
|---|---|---|---|
| outbound UDP toelaten | ... | ... | ... |
| alleen noodzakelijke UDP naar vaste serverrol toelaten | ... | ... | ... |
| UDP/41641 naar alle clients inbound openen | ... | ... | ... |
| port forwarding naar deze tijdelijke VM | ... | ... | ... |
| DERP blokkeren om direct af te dwingen | ... | ... | ... |
| niets wijzigen en relay accepteren | ... | ... | ... |

Je advies moet rekening houden met:

- tijdelijke lifecycle van de VM;
- geen controle over CGNAT of campus-NAT;
- minimaal aanvalsoppervlak;
- beschikbaarheid van DERP als fallback;
- logging en documentatie;
- gemeten performance, niet alleen aannames.

---

## 24. Stap 17: analyseer MTU en beschikbaarheid

Voer een eenvoudige, niet-destructieve test uit.

Op Windows:

```text
ping -n 4 -l 1200 <VM-TAILSCALE-IP>
```

Op Linux:

```text
ping -c 4 -s 1200 <VM-TAILSCALE-IP>
```

Beantwoord:

1. Werken gewone en grotere pings?
2. Bewijst dit dat elke mogelijke pakketgrootte werkt?
3. Welke symptomen uit de cursus passen bij een MTU-probleem?
4. Waarom kan een aanvaller of netwerkbeheerder beschikbaarheid verstoren zonder de VPN-inhoud te ontsleutelen?

---

## 25. Foutscenario's

### Scenario A: peer zichtbaar, HTTP faalt

Onderzoek in deze volgorde:

```text
tailscale ping <VM>
ss -lntp | grep ':8080'
curl http://<VM-TAILSCALE-IP>:8080
cat "$HOME/ch7-http.log"
```

Mogelijke oorzaken:

- webserverproces is gestopt;
- webserver bindt aan verkeerd adres;
- verkeerde poort;
- ACL of host firewall blokkeert TCP/8080;
- verkeerde peer getest.

### Scenario B: alleen DERP

Onderzoek:

```text
tailscale netcheck
tailscale ping --c 10 --until-direct=false <VM>
tailscale status
```

Mogelijke verklaringen:

- outbound UDP wordt beperkt;
- moeilijke NAT aan een of beide kanten;
- endpointmapping varieert;
- directe onderhandeling is nog bezig;
- netwerk is net gewisseld;
- een tijdelijke netwerkstoring.

### Scenario C: Tailscale-IP werkt, MagicDNS-naam niet

Interpretatie:

> De data-planeverbinding kan werken terwijl naamresolutie fout zit. Onderzoek MagicDNS en DNS apart van bereikbaarheid.

### Scenario D: performance is laag terwijl het pad direct is

Onderzoek ook:

- wifi-signaal en interferentie;
- packet loss en jitter;
- CPU op laptop en VM;
- richting van de transfer;
- congestie;
- MTU;
- applicatie in plaats van alleen de VPN.

---

## 26. Opruimen

Stop alleen de processen die je in deze workshop startte:

```text
test -f "$HOME/ch7-http.pid" && kill "$(cat "$HOME/ch7-http.pid")"
test -f "$HOME/ch7-iperf3.pid" && kill "$(cat "$HOME/ch7-iperf3.pid")"
```

Controleer:

```text
ss -lntp | grep -E ':8080|:5201'
```

Verwijder de VM alleen uit je tailnet als de docent dat vraagt. Voer geen `tailscale logout` uit als de VM in een volgende workshop verder gebruikt wordt.

---

## 27. In te dienen

Lever één technisch verslag in met:

1. topologie met underlay- en overlayadressen;
2. server- en clientinventaris;
3. bewijs van Tailscale-installatie zonder secrets;
4. bewijs dat de webdienst alleen op het Tailscale-IP luistert;
5. Devbit-`netcheck`, pad-, latency- en throughputmeting;
6. eduroam/campusroam-`netcheck`, pad-, latency- en throughputmeting;
7. vergelijking van beide fysieke netwerken;
8. uitleg van endpoint discovery, NAT mapping en hole punching;
9. bewijs en interpretatie van direct, peer relay of DERP;
10. capturesamenvatting van `tailscale0` versus fysieke interface;
11. positieve en negatieve securitytests;
12. bewijs dat dit een split-tunnelopzet is;
13. MagicDNS-test en DNS-privacyanalyse;
14. zichtbaarheidstabel per beheerder;
15. control-plane/data-planeclassificatie;
16. niet-uitgevoerd firewall- en port-forwardingadvies;
17. foutanalyse indien iets niet werkte;
18. eindconclusie.

Neem geen secrets of ongeredigeerde publieke IP-adressen op.

---

## 28. Eindvraag

Sluit af met een antwoord op:

> Waarom kan de Debian-server vanaf zowel Devbit als eduroam/campusroam via hetzelfde Tailscale-adres bereikbaar blijven, terwijl het werkelijke datapad, de NAT mapping, de zichtbare metadata en de performance toch kunnen veranderen?
