# Thuisoefening 1 - Modeloplossing voor studenten

## 1. Korte samenvatting

Het netwerk van **Asteria Logistics** werkt technisch voor basisconnectiviteit, maar is nog niet enterprise-ready.

De belangrijkste problemen zijn:

- IoT-toestellen hebben te brede toegang;
- guests kunnen managementadressen bereiken;
- de interne ERP-server is rechtstreeks gepubliceerd via static NAT;
- het warehouse-subnet is te klein;
- managementtoegang is onvoldoende beveiligd;
- trunks zijn te breed geconfigureerd;
- de native VLAN blijft VLAN 1;
- `R1-HQ` is een single point of failure.

---

## 2. Topologie

| Van | Naar | Verbinding | Functie |
|---|---|---|---|
| `R1-HQ G0/0` | `SW1-DIST G0/1` | trunk | router-on-a-stick |
| `R1-HQ G0/1` | `ISP-SERVER Fa0` | routed link | internet/ISP |
| `SW1-DIST G0/2` | `SW2-FLOOR G0/1` | trunk | distributie naar access |
| `SW1-DIST Fa0/10` | `SRV-ERP Fa0` | access | ERP-server |
| `SW2-FLOOR Fa0/1` | `PC-OFFICE` | access | office |
| `SW2-FLOOR Fa0/2` | `PC-WAREHOUSE` | access | warehouse |
| `SW2-FLOOR Fa0/3` | `PC-GUEST` | access | guest |
| `SW2-FLOOR Fa0/4` | `PC-IOT` | access | IoT |
| `SW2-FLOOR Fa0/5` | `PC-ADMIN` | access | management/admin |

Belangrijke vaststelling:

`R1-HQ` is kritisch omdat dit toestel inter-VLAN routing, DHCP, NAT/PAT, static NAT en ACL-filtering uitvoert.

---

## 3. VLAN-tabel

| VLAN | Naam | Poorten | Functie | Opmerking |
|---:|---|---|---|---|
| 10 | `OFFICE` | `SW2 Fa0/1` | kantoorpc's | interne gebruikers |
| 20 | `WAREHOUSE` | `SW2 Fa0/2` | magazijntoestellen | subnet is te klein |
| 40 | `GUEST` | `SW2 Fa0/3` | gasten | laag vertrouwd |
| 50 | `ERP_SERVERS` | `SW1 Fa0/10` | ERP-server | kritisch systeem |
| 60 | `IOT` | `SW2 Fa0/4` | camera's/scanners | laag tot middelmatig vertrouwd |
| 99 | `MGMT` | `SW2 Fa0/5`, switch-SVI's | management | zeer kritisch |

Trunks:

| Toestel | Poort | Naar | Vaststelling |
|---|---|---|---|
| `SW1-DIST` | `G0/1` | `R1-HQ` | trunk, alle VLAN's toegelaten |
| `SW1-DIST` | `G0/2` | `SW2-FLOOR` | trunk, alle VLAN's toegelaten |
| `SW2-FLOOR` | `G0/1` | `SW1-DIST` | trunk, alle VLAN's toegelaten |

Risico:

Alle VLAN's worden over de trunks vervoerd. Dat is technisch eenvoudig, maar niet ideaal. In een enterprise netwerk beperk je trunks tot noodzakelijke VLAN's.

---

## 4. IP-adresplan

| VLAN | Subnet | Gateway | DHCP/statisch | Opmerking |
|---:|---|---|---|---|
| 10 | `10.20.10.0/24` | `10.20.10.1` | DHCP | voldoende groot |
| 20 | `10.20.20.0/29` | `10.20.20.1` | DHCP | te klein voor groei |
| 40 | `10.20.40.0/24` | `10.20.40.1` | DHCP | guests |
| 50 | `10.20.50.0/24` | `10.20.50.1` | server statisch | ERP-server |
| 60 | `10.20.60.0/24` | `10.20.60.1` | DHCP | IoT |
| 99 | `10.20.99.0/24` | `10.20.99.1` | DHCP en statisch | management |

Vaste adressen:

| Toestel | IP-adres | Functie |
|---|---|---|
| `SRV-ERP` | `10.20.50.10` | interne ERP-server |
| `SW1-DIST` | `10.20.99.11` | management |
| `SW2-FLOOR` | `10.20.99.12` | management |
| `R1-HQ G0/1` | `198.51.100.1` | buiteninterface |
| `ISP-SERVER` | `198.51.100.2` | ISP/internet |

Belangrijke vaststelling:

VLAN 20 gebruikt `10.20.20.0/29`. Dat levert maar zes bruikbare hostadressen op. Voor een groeiend magazijn met scanners, tablets en andere toestellen is dat niet schaalbaar.

---

## 5. Routing, DHCP en NAT/PAT

| Onderdeel | Locatie | Bewijs | Opmerking |
|---|---|---|---|
| Inter-VLAN routing | `R1-HQ` | subinterfaces `G0/0.x` | router-on-a-stick |
| DHCP | `R1-HQ` | DHCP-pools in running-config | router deelt adressen uit |
| NAT/PAT | `R1-HQ` | `ip nat inside source list 1 interface g0/1 overload` | internettoegang |
| Static NAT/port forwarding | `R1-HQ` | `ip nat inside source static tcp 10.20.50.10 80 198.51.100.1 80` | ERP-webdienst publiek bereikbaar |
| Default route | `R1-HQ` | `ip route 0.0.0.0 0.0.0.0 198.51.100.2` | route naar ISP |

Belangrijke vaststelling:

De ERP-server staat in het interne servernetwerk, maar is via static NAT bereikbaar vanaf de buitenkant. Dat is een risico. Een publiek bereikbare dienst hoort beter in een DMZ of achter een reverse proxy.

---

## 6. Zoneschema

| Zone | VLAN/subnet | Vertrouwensniveau | Waarom? |
|---|---|---|---|
| Office | VLAN 10, `10.20.10.0/24` | gemiddeld | gekende interne gebruikers |
| Warehouse | VLAN 20, `10.20.20.0/29` | gemiddeld | operationele toestellen |
| Guest | VLAN 40, `10.20.40.0/24` | laag | onbekende toestellen |
| ERP servers | VLAN 50, `10.20.50.0/24` | hoog | kritieke bedrijfsapplicatie |
| IoT | VLAN 60, `10.20.60.0/24` | laag tot middelmatig | toestellen zijn vaak moeilijker te beheren |
| Management | VLAN 99, `10.20.99.0/24` | zeer hoog | beheer van netwerktoestellen |
| Internet | `198.51.100.0/30` en verder | zeer laag | externe omgeving |

Belangrijke vaststelling:

IoT en Guest zijn lager vertrouwde zones. Ze mogen niet breed kunnen communiceren met servers of management.

---

## 7. ACL- en managementanalyse

### 7.1 Guest ACL

Relevante configuratie:

```text
ip access-list extended GUEST_FILTER
 permit udp any eq bootpc any eq bootps
 deny ip 10.20.40.0 0.0.0.255 10.20.50.0 0.0.0.255
 permit ip 10.20.40.0 0.0.0.255 any
```

Toegepast op:

```text
interface g0/0.40
 ip access-group GUEST_FILTER in
```

Analyse:

| Wat? | Resultaat |
|---|---|
| Guest naar ERP-server | geblokkeerd |
| Guest naar internet | toegelaten |
| Guest naar management | toegelaten |

Probleem:

De ACL blokkeert alleen het ERP-servernetwerk. Het managementnetwerk wordt niet geblokkeerd. Daardoor kunnen guests managementadressen bereiken.

### 7.2 Managementtoegang

Relevante configuratie:

```text
line vty 0 4
 login local
 transport input ssh
```

Problemen:

- Er is geen beperking tot het managementsubnet.
- Gewone clients kunnen managementinterfaces bereiken.
- Het wachtwoord is didactisch zwak.

---

## 8. Securityregelmatrix

Gewenst gedrag:

| Bronzone | Doelzone | Gewenst gedrag | Waarom? |
|---|---|---|---|
| Office | ERP server | toegelaten | kantoor gebruikt ERP |
| Warehouse | ERP server | toegelaten of beperkt | magazijn gebruikt ERP |
| Guest | ERP server | geblokkeerd | guests zijn laag vertrouwd |
| Guest | Internet | toegelaten | gasten hebben internet nodig |
| Guest | Management | geblokkeerd | guests mogen geen beheerinterfaces bereiken |
| IoT | ERP server | geblokkeerd of zeer beperkt | IoT heeft meestal geen brede servertoegang nodig |
| IoT | Management | geblokkeerd | IoT mag netwerktoestellen niet bereiken |
| Users | Management | geblokkeerd | gewone gebruikers beheren geen netwerk |
| Admin | Management | toegelaten | beheerder moet toestellen kunnen beheren |
| Internet | ERP server | alleen via gecontroleerde publicatie | geen rechtstreekse interne serverpublicatie |

Afwijkingen:

| Afwijking | Waarom problematisch? |
|---|---|
| Guest kan management bereiken | laag vertrouwde toestellen kunnen beheerinterfaces scannen |
| IoT kan ERP-server bereiken | IoT-toestellen krijgen te brede toegang |
| IoT kan management bereiken | laag vertrouwde toestellen kunnen kritieke infrastructuur bereiken |
| Office kan management bereiken | gewone gebruikers hebben te veel zicht op beheerinterfaces |
| ERP is publiek bereikbaar via static NAT | interne server wordt rechtstreeks blootgesteld |

---

## 9. Testplan met resultaten

| Test | Verwacht vanuit enterprise-standpunt | Werkelijk resultaat | Conclusie |
|---|---|---|---|
| `PC-OFFICE` naar `10.20.50.10` | werkt | werkt | office kan ERP gebruiken |
| `PC-WAREHOUSE` naar `10.20.50.10` | werkt | werkt | warehouse kan ERP gebruiken |
| `PC-GUEST` naar `198.51.100.2` | werkt | werkt | guest heeft internet |
| `PC-GUEST` naar `10.20.50.10` | werkt niet | werkt niet | ACL blokkeert guest naar ERP |
| `PC-GUEST` naar `10.20.99.11` | werkt niet | werkt | securityprobleem |
| `PC-IOT` naar `10.20.50.10` | werkt niet of beperkt | werkt | securityprobleem |
| `PC-IOT` naar `10.20.99.12` | werkt niet | werkt | ernstig securityprobleem |
| `PC-OFFICE` naar `10.20.99.11` | werkt niet | werkt | management te breed bereikbaar |
| `PC-ADMIN` naar `10.20.99.11` | werkt | werkt | admin kan beheren |
| `ISP-SERVER` naar `http://198.51.100.1` | alleen via veilige publicatie | werkt | ERP wordt rechtstreeks gepubliceerd |

Belangrijke vaststelling:

Sommige succesvolle testen zijn juist een probleem. Vooral toegang van Guest of IoT naar management en de publieke toegang naar ERP tonen dat het netwerk securitymatig niet goed gescheiden is.

---

## 10. Risico- en verbeterpuntenlijst

| Risico | Impact | Bewijs of test | Mogelijke verbetering |
|---|---|---|---|
| Guest kan management bereiken | hoog | `PC-GUEST` naar `10.20.99.11` werkt | blokkeer guest naar interne subnetten of minstens management |
| IoT kan ERP-server bereiken | hoog | `PC-IOT` naar `10.20.50.10` werkt | IoT alleen noodzakelijke diensten toelaten |
| IoT kan management bereiken | hoog | `PC-IOT` naar `10.20.99.12` werkt | blokkeer IoT naar management |
| Office kan management bereiken | middel/hoog | `PC-OFFICE` naar `10.20.99.11` werkt | management alleen vanaf adminzone |
| ERP is publiek bereikbaar via static NAT | hoog | `http://198.51.100.1` toont ERP | gebruik DMZ of reverse proxy |
| Warehouse subnet is te klein | middel | VLAN 20 is `/29` | groter subnet voorzien |
| Trunks laten alle VLAN's toe | middel | `show interfaces trunk` | allowed VLANs beperken |
| Native VLAN is VLAN 1 | middel | trunkconfiguratie | ongebruikte native VLAN gebruiken |
| Router is single point of failure | hoog | alle kritieke functies op `R1-HQ` | redundantie of functies spreiden |
| Geen monitoring/logging zichtbaar | middel | geen logging- of monitoringplan zichtbaar | monitoring en logging voorzien |

---

## 11. Concrete verbeterpunten

| Verbeterpunt | Welk probleem lost dit op? | Hoe test je dit? |
|---|---|---|
| Blokkeer Guest naar alle interne subnetten | guest kan management bereiken | `PC-GUEST` naar `10.20.99.11` moet falen |
| Laat Guest alleen naar internet toe | laag vertrouwde toegang beperken | `PC-GUEST` naar `198.51.100.2` blijft werken |
| Blokkeer IoT naar Management | IoT kan netwerktoestellen bereiken | `PC-IOT` naar `10.20.99.12` moet falen |
| Beperk IoT naar ERP | IoT heeft te brede servertoegang | alleen noodzakelijke poorten/hosts toelaten |
| Beperk VTY tot management/adminsubnet | gewone users kunnen beheerinterfaces bereiken | `PC-OFFICE` VTY naar switch moet falen |
| Verplaats publieke ERP-toegang naar DMZ/reverse proxy | interne server is rechtstreeks gepubliceerd | externe test gaat naar proxy/DMZ, niet rechtstreeks intern |
| Vergroot VLAN 20-subnet | warehouse kan niet groeien | nieuw adresplan met voldoende hosts |
| Beperk trunk allowed VLANs | onnodige VLAN-verspreiding | `show interfaces trunk` controleren |
| Gebruik native VLAN 999 | native VLAN 1 vermijden | trunkconfiguratie controleren |
| Voorzie redundantie voor kritieke functies | `R1-HQ` is single point of failure | ontwerp toont alternatief pad of tweede toestel |

---

## 12. Mogelijke verbeterde ACL's

### 12.1 Guest beperken

```text
configure terminal
no ip access-list extended GUEST_FILTER

ip access-list extended GUEST_FILTER
 remark Guests may only access internet
 permit udp any eq bootpc any eq bootps
 deny ip 10.20.40.0 0.0.0.255 10.20.0.0 0.0.255.255
 permit ip 10.20.40.0 0.0.0.255 any
exit

interface g0/0.40
 ip access-group GUEST_FILTER in
end
```

Verwacht:

- guest naar ERP: geblokkeerd;
- guest naar management: geblokkeerd;
- guest naar internet: toegelaten;
- DHCP blijft werken.

### 12.2 IoT beperken

Een strenge voorbeeldregel:

```text
configure terminal
ip access-list extended IOT_FILTER
 remark IoT should not access management or broad internal networks
 permit udp any eq bootpc any eq bootps
 deny ip 10.20.60.0 0.0.0.255 10.20.99.0 0.0.0.255
 deny ip 10.20.60.0 0.0.0.255 10.20.50.0 0.0.0.255
 permit ip 10.20.60.0 0.0.0.255 any
exit

interface g0/0.60
 ip access-group IOT_FILTER in
end
```

Let op:

In een echte enterprise omgeving zou je IoT niet zomaar `permit ip ... any` geven. Je zou bepalen welke diensten echt nodig zijn, bijvoorbeeld DNS, NTP of verkeer naar een specifieke controller.

---

## 13. Managementtoegang verbeteren

Voorbeeld:

```text
configure terminal
ip access-list standard MGMT_ONLY
 permit 10.20.99.0 0.0.0.255
 deny any
exit

line vty 0 4
 access-class MGMT_ONLY in
 transport input ssh
exit
end
```

Effect:

- alleen management/adminsubnet mag VTY gebruiken;
- SSH-management is beperkt tot de management/adminzone.

---

## 14. Publicatie van ERP verbeteren

De huidige static NAT:

```text
ip nat inside source static tcp 10.20.50.10 80 198.51.100.1 80
```

Probleem:

De interne ERP-server wordt rechtstreeks bereikbaar gemaakt via het publieke adres van de router.

Betere enterprise-aanpak:

- plaats publieke webdiensten in een DMZ;
- gebruik een reverse proxy;
- laat alleen noodzakelijke poorten toe;
- log externe toegang;
- gebruik authenticatie;
- scheid publieke toegang van het interne servernetwerk.

Voor hoofdstuk 1 moeten studenten dit vooral herkennen als risico. De technische uitwerking volgt later in het OPO bij reverse proxy en identity provider.

---

## 15. Modelconclusie

Het netwerk van Asteria Logistics werkt technisch voor basisconnectiviteit. Clients krijgen via DHCP een IP-adres, inter-VLAN routing werkt en interne gebruikers kunnen de ERP-server bereiken. Ook internettoegang via NAT/PAT werkt.

Toch is het netwerk nog niet enterprise-ready. De belangrijkste problemen zijn de te brede toegang tussen zones, vooral vanuit Guest en IoT. Guests kunnen managementadressen bereiken en IoT-toestellen kunnen zowel de ERP-server als managementadressen bereiken. Daarnaast is de ERP-webdienst rechtstreeks gepubliceerd via static NAT, zonder DMZ of reverse proxy. Dat vergroot het risico bij een kwetsbaarheid op de server.

Ook de beheerbaarheid en betrouwbaarheid zijn onvoldoende. Managementtoegang is niet voldoende beperkt, trunks laten alle VLAN's toe en VLAN 20 gebruikt een te klein subnet voor een groeiend magazijn. `R1-HQ` is bovendien een single point of failure voor routing, DHCP, NAT en filtering.

Conclusie: het netwerk is technisch werkend, maar niet professioneel genoeg ontworpen voor verdere groei. De prioriteit ligt bij betere zonescheiding, strengere managementtoegang, veilige publicatie van de ERP-dienst, een schaalbaarder IP-plan en betere documentatie.
