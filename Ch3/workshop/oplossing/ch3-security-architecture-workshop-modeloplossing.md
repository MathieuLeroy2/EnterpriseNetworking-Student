# Workshop 3 - Security zoning en DMZ-design

## Modeloplossing voor studenten

## 1. Korte samenvatting

Het netwerk van **BluePeak Services** bevat verschillende zones die typisch zijn voor een enterprise-omgeving:

- Staff;
- Finance;
- IT;
- Servers;
- Guests;
- IoT;
- DMZ;
- Management;
- Internet.

De technische basis is aanwezig, maar de securityarchitectuur is in de beginsituatie onvoldoende strikt.

De belangrijkste vaststellingen zijn:

- het guest VLAN is onvoldoende geisoleerd;
- managementtoegang is te breed bereikbaar;
- IoT-toestellen kunnen te veel interne systemen bereiken;
- de publieke webdienst moet duidelijk in een DMZ staan;
- DMZ-verkeer naar intern is te breed;
- finance-systemen zijn onvoldoende apart beschermd;
- bestaande ACL's zijn onvolledig of te breed;
- er ontbreekt een duidelijke firewallregelmatrix;
- verboden verkeersstromen worden onvoldoende getest.

Belangrijke conclusie:

> Het netwerk werkt technisch, maar het securitybeleid is niet scherp genoeg. Een enterprise-netwerk moet niet alleen verbinding voorzien, maar ook kunnen aantonen waarom bepaalde verbindingen wel of niet toegelaten zijn.

---

## 2. VLAN- en subnetoverzicht

| VLAN | Naam | Subnet | Gateway | Doel |
|---:|---|---|---|---|
| 10 | `STAFF` | `10.30.10.0/24` | `10.30.10.1` | gewone medewerkers |
| 20 | `FINANCE` | `10.30.20.0/24` | `10.30.20.1` | finance-afdeling |
| 30 | `IT` | `10.30.30.0/24` | `10.30.30.1` | IT-beheerders |
| 40 | `SERVERS` | `10.30.40.0/24` | `10.30.40.1` | interne servers |
| 50 | `GUESTS` | `10.30.50.0/24` | `10.30.50.1` | gasten |
| 60 | `IOT` | `10.30.60.0/24` | `10.30.60.1` | IoT-toestellen |
| 70 | `DMZ` | `10.30.70.0/24` | `10.30.70.1` | publieke diensten |
| 99 | `MGMT` | `10.30.99.0/24` | `10.30.99.1` | managementinterfaces |

Analyse:

De VLAN-indeling is logisch als startpunt. De zones zijn duidelijk herkenbaar. Vooral VLAN 50, 60, 70 en 99 vragen strenge regels, omdat ze respectievelijk guests, IoT, DMZ en management bevatten.

Sterke conclusie:

> De segmentatie bestaat technisch, maar segmentatie is pas security wanneer er ook beleid tussen de zones wordt afgedwongen.

---

## 3. Zones en vertrouwensniveaus

| Zone | VLAN's of subnetten | Vertrouwensniveau | Waarom? |
|---|---|---|---|
| Internet | `203.0.113.0/30` en extern | zeer laag | niet onder controle van BluePeak |
| DMZ | VLAN 70, `10.30.70.0/24` | laag tot middel | publiek bereikbaar, dus verhoogd risico |
| Guests | VLAN 50, `10.30.50.0/24` | laag | toestellen zijn onbekend of onbeheerd |
| IoT | VLAN 60, `10.30.60.0/24` | laag tot middel | toestellen zijn vaak beperkt beheerbaar |
| Staff | VLAN 10, `10.30.10.0/24` | middel | interne gebruikers, maar geen beheerders |
| Finance | VLAN 20, `10.30.20.0/24` | middel tot hoog | gevoelige bedrijfsdata |
| Servers | VLAN 40, `10.30.40.0/24` | hoog | interne applicaties en data |
| IT | VLAN 30, `10.30.30.0/24` | hoog | beheerderswerkstations |
| Management | VLAN 99, `10.30.99.0/24` | zeer hoog | toegang tot netwerktoestellen |

Analyse:

Niet elk intern VLAN is even betrouwbaar. Guests en IoT zijn laag vertrouwd, ook al zitten ze technisch binnen het bedrijfsnetwerk. Management heeft het hoogste beschermingsniveau nodig.

---

## 4. Trust boundaries

| Trust boundary | Waarom is dit een grens? | Controle nodig? |
|---|---|---|
| Internet - DMZ | publieke toegang naar bedrijfsdienst | firewallregel en logging |
| Internet - intern netwerk | externe hosts mogen intern niet bereiken | standaard blokkeren |
| DMZ - intern netwerk | DMZ kan gecompromitteerd worden | alleen expliciete backendtoegang |
| Guests - intern netwerk | guesttoestellen zijn onbeheerd | intern blokkeren |
| IoT - servers | IoT is lager vertrouwd | alleen noodzakelijke dienst |
| Staff - management | gewone gebruikers beheren geen toestellen | blokkeren |
| IT - management | IT moet beheren | toelaten en loggen |
| Finance - servers | gevoelige bedrijfsprocessen | specifieke appregels |

Sterke conclusie:

> De belangrijkste trust boundaries liggen rond Guests, IoT, DMZ en Management. Als daar geen filtering gebeurt, is de zone-indeling onvoldoende.

---

## 5. DMZ-beoordeling

| Dienst | Huidige zone | Gewenste zone | Toegang vanaf internet | Opmerking |
|---|---|---|---|---|
| Publieke website | DMZ of foutief intern | DMZ | alleen HTTPS | publiek, dus niet in intern servernetwerk |
| Interne applicatie `SRV-APP` | Servers | Servers | nee | alleen interne gebruikers |
| Finance-app `SRV-FIN` | Servers | bij voorkeur Finance/Servers met strikte policy | nee | gevoelige data |
| Jump host | Management | Management | nee vanaf internet | alleen IT |

Analyse:

Een publieke webdienst hoort in de DMZ. Als port forwarding of NAT naar een interne server in VLAN 40 wijst, is dat een belangrijk risico. Bij misbruik van de publieke server krijgt een aanvaller dan sneller toegang tot het interne servernetwerk.

Gewenst gedrag:

- Internet mag HTTPS naar `SRV-WEB-DMZ`.
- Internet mag niet naar `SRV-APP` of `SRV-FIN`.
- DMZ mag niet vrij naar interne subnetten.
- IT mag de DMZ beheren via gecontroleerde beheerkanalen.

---

## 6. Analyse van bestaande regels

| ACL of regel | Plaats | Bedoeling | Probleem of risico |
|---|---|---|---|
| `GUEST_WEAK` | guest-interface inbound | guests beperken | blokkeert alleen management, niet alle interne zones |
| `DMZ_WEAK` | DMZ-interface inbound | DMZ-verkeer toelaten | laat DMZ breed naar intern toe |
| management allow-regels | onduidelijk of te breed | beheer mogelijk maken | staff of guests kunnen management bereiken |
| brede permit-regels | onderaan of bovenaan ACL | verkeer laten werken | niet volgens least privilege |
| ontbrekende internet-deny naar intern | edge/firewall | perimeterbeveiliging | internet kan mogelijk te veel bereiken |

Analyse:

De bestaande regels zijn te veel gegroeid vanuit "het moet werken". Ze vertrekken niet vanuit een duidelijke firewallregelmatrix. Daardoor zijn sommige zones technisch gescheiden, maar niet voldoende beveiligd.

Sterke conclusie:

> De ACL's bevatten enkele nuttige ideeën, maar ze zijn geen volledig securitybeleid. Vooral guest-, DMZ-, IoT- en managementverkeer moeten opnieuw vanuit least privilege ontworpen worden.

---

## 7. Gewenste firewallregelmatrix

| Bronzone | Doelzone | Dienst | Actie | Reden |
|---|---|---|---|---|
| Staff | `SRV-APP` | HTTPS | allow | medewerkers gebruiken interne applicatie |
| Staff | Management | any | deny | medewerkers beheren geen netwerktoestellen |
| Staff | Finance-server | any tenzij nodig | deny | finance-data beperken |
| Finance | `SRV-FIN` | HTTPS of apppoort | allow | financeproces |
| Finance | Management | any | deny | geen beheerrechten |
| IT | Management | SSH/HTTPS | allow | netwerkbeheer |
| IT | Servers | HTTP/HTTPS | allow beperkt | praktische servervalidatie in Packet Tracer |
| IT | DMZ | HTTP/HTTPS | allow beperkt | praktische DMZ-validatie in Packet Tracer |
| Guests | Internet | DNS/HTTP/HTTPS | allow | gastinternet |
| Guests | andere interne zones | any | deny | guests isoleren, maar eigen gateway bereikbaar houden |
| IoT | `SRV-APP` of specifieke collector | specifieke poort | allow beperkt | devicefunctie |
| IoT | Management | any | deny | beheer beschermen |
| IoT | Servers algemeen | any | deny | laterale beweging beperken |
| Internet | `SRV-WEB-DMZ` | HTTPS | allow | publieke website |
| Internet | Internal servers | any | deny | intern netwerk beschermen |
| DMZ | Internal | any standaard | deny | compromis beperken |
| DMZ | Backend | specifieke poort indien nodig | allow beperkt | alleen noodzakelijke koppeling |
| DMZ | Management | any | deny | beheer beschermen |

Belangrijk:

Elke allow-regel moet gekoppeld zijn aan een duidelijke behoefte. Alles wat niet nodig is, wordt niet toegelaten.

---

## 8. Testplan

| Test | Bron | Doel | Dienst | Verwacht | Conclusie |
|---|---|---|---|---|---|
| Staff naar intranet | `PC-STAFF` | `SRV-APP` | HTTPS | werkt | noodzakelijke bedrijfsapp |
| Staff naar management | `PC-STAFF` | `10.30.99.11` | SSH/HTTPS | faalt | staff mag niet beheren |
| Finance naar finance-app | `PC-FINANCE` | `SRV-FIN` | appdienst | werkt | financeproces |
| Finance naar management | `PC-FINANCE` | management-IP | SSH/HTTPS | faalt | geen beheerrechten |
| Guest naar internet | `PC-GUEST` | ISP/web | HTTP/HTTPS | werkt | gastinternet |
| Guest naar server | `PC-GUEST` | `SRV-APP` | ICMP/HTTP | faalt | guest isolatie |
| Guest naar management | `PC-GUEST` | management-IP | SSH/HTTPS | faalt | beheer beschermd |
| IT naar management | `PC-IT` | switch/router management | SSH | werkt | IT-beheer |
| IT naar server | `PC-IT` | `SRV-APP` | HTTP/HTTPS | werkt | servervalidatie in Packet Tracer |
| IoT naar management | `CAM-IOT` | management-IP | SSH/HTTPS | faalt | IoT laag vertrouwd |
| IoT naar server | `CAM-IOT` | specifieke server | specifieke poort | alleen indien nodig | least privilege |
| Internet naar DMZ-web | ISP/externe host | `SRV-WEB-DMZ` | HTTPS | werkt | publieke dienst |
| Internet naar interne app | ISP/externe host | `SRV-APP` | HTTP/HTTPS | faalt | intern niet publiek |
| DMZ naar management | `SRV-WEB-DMZ` | management-IP | SSH/HTTPS | faalt | DMZ beperkt |
| DMZ naar intern servernetwerk | `SRV-WEB-DMZ` | `SRV-APP` | any | faalt tenzij expliciet nodig | laterale beweging beperkt |

Analyse:

Dit testplan test zowel toegelaten als verboden verkeer. Dat is noodzakelijk om securitybeleid te bewijzen.

---

## 9. Risico's en verbeterpunten

| Vaststelling | Risico | Impact | Mogelijke verbetering |
|---|---|---|---|
| Guest kan interne servers bereiken | onbekende toestellen kunnen interne systemen scannen | hoog | guests blokkeren naar andere interne zones |
| Staff kan management bereiken | gewone gebruikers kunnen beheerinterfaces aanvallen | hoog | management alleen vanaf IT of jump host |
| DMZ kan breed naar intern | compromis van DMZ-server geeft toegang intern | hoog | DMZ naar intern default deny |
| IoT kan breed naar servers | laag vertrouwde toestellen krijgen te veel toegang | middel/hoog | IoT alleen naar specifieke dienst |
| Publieke dienst staat intern | internetaanval raakt intern servernetwerk | hoog | publieke dienst in DMZ plaatsen |
| Finance-app staat zonder specifieke policy in servernetwerk | gevoelige data te breed bereikbaar | hoog | aparte finance-regels of aparte zone |
| `permit ip any any` zonder motivatie | te brede toegang blijft bestaan | hoog | vervangen door specifieke allow-regels |
| Geen deny-tests | securityproblemen blijven onzichtbaar | middel | testplan met verboden stromen |
| Geen logging op kritieke grenzen | incidenten moeilijk onderzoeken | middel | logging voorzien op DMZ, guest en management |
| ACL's niet gedocumenteerd | beheer wordt onveilig | middel | regelmatrix met reden en eigenaar |

---

## 10. Mogelijke technische verbeteringen

### 10.1 Guest isoleren

Conceptueel:

```text
deny   guest -> internal
permit guest -> internet
```

Mogelijke ACL-vertaling:

```text
ip access-list extended GUEST_IN
 permit ip 10.30.50.0 0.0.0.255 host 10.30.50.1
 deny ip 10.30.50.0 0.0.0.255 10.30.10.0 0.0.0.255
 deny ip 10.30.50.0 0.0.0.255 10.30.20.0 0.0.0.255
 deny ip 10.30.50.0 0.0.0.255 10.30.30.0 0.0.0.255
 deny ip 10.30.50.0 0.0.0.255 10.30.40.0 0.0.0.255
 deny ip 10.30.50.0 0.0.0.255 10.30.60.0 0.0.0.255
 deny ip 10.30.50.0 0.0.0.255 10.30.70.0 0.0.0.255
 deny ip 10.30.50.0 0.0.0.255 10.30.99.0 0.0.0.255
 permit ip 10.30.50.0 0.0.0.255 any
```

Test:

- `PC-GUEST` naar internet werkt.
- `PC-GUEST` naar `SRV-APP` faalt.
- `PC-GUEST` naar management faalt.
- `PC-GUEST` naar de eigen gateway `10.30.50.1` werkt.

### 10.2 Management beperken

Conceptueel:

```text
allow IT -> Management SSH/HTTPS
deny  all others -> Management
```

Test:

- `PC-IT` kan management bereiken.
- `PC-STAFF` kan management niet bereiken.
- `PC-GUEST` kan management niet bereiken.

### 10.3 DMZ beperken

Conceptueel:

```text
allow Internet -> DMZ web HTTPS
deny  Internet -> Internal
deny  DMZ -> Management
deny  DMZ -> Internal tenzij expliciet nodig
```

Test:

- externe host kan de DMZ-webserver bereiken via HTTPS;
- externe host kan interne servers niet bereiken;
- DMZ-server kan management niet bereiken;
- DMZ-server kan niet breed naar servers.

### 10.4 IoT beperken

Conceptueel:

```text
allow IoT -> specifieke server/dienst
deny  IoT -> Management
deny  IoT -> Servers algemeen
```

Test:

- IoT werkt alleen voor de noodzakelijke dienst;
- IoT kan management niet bereiken;
- IoT kan niet vrij naar alle servers.

---

## 11. Prioriteiten

Een realistische prioriteitsvolgorde:

1. Guest isoleren van alle interne subnetten.
2. Managementtoegang beperken tot IT of jump host.
3. Publieke webdienst correct in DMZ plaatsen.
4. DMZ-verkeer naar intern standaard blokkeren.
5. IoT-verkeer beperken tot noodzakelijke diensten.
6. Finance-applicatie specifieker beschermen.
7. Brede `permit ip any any`-regels vervangen door specifieke regels.
8. Testplan en regelmatrix documenteren.
9. Logging voorzien op guest-, DMZ- en managementgrenzen.

Waarom deze volgorde?

De eerste risico's hebben de grootste impact: onbekende toestellen, beheerinterfaces en publieke diensten. Daarna verfijn je interne toegang en documentatie.

---

## 12. Modelconclusie

Het netwerk van BluePeak Services heeft een bruikbare technische basis. De VLAN's en zones zijn herkenbaar: Staff, Finance, IT, Servers, Guests, IoT, DMZ en Management. Dat is positief, want het netwerk is al logisch op te delen.

Toch is het netwerk securitymatig nog niet enterprise-ready. Het guest VLAN is onvoldoende geisoleerd, waardoor onbekende toestellen interne systemen kunnen bereiken. Managementtoegang is te breed bereikbaar en moet beperkt worden tot IT of een jump host. De publieke webdienst moet duidelijk in een DMZ staan en mag geen rechtstreekse toegang naar het interne servernetwerk krijgen. Ook IoT-verkeer is te breed en moet beperkt worden tot noodzakelijke diensten. Finance-systemen verdienen specifiekere bescherming omdat ze gevoelige data bevatten.

De belangrijkste verbeteringen zijn: een firewallregelmatrix volgens least privilege opstellen, guests blokkeren naar andere interne zones, management alleen vanaf IT toelaten, DMZ-verkeer naar intern standaard blokkeren, IoT-verkeer beperken en alle kritieke stromen testen.

Eindconclusie:

> Het netwerk werkt technisch, maar het securitybeleid is nog te breed en onvoldoende gedocumenteerd. Pas wanneer de zones, trust boundaries, DMZ-regels en testresultaten duidelijk aantonen welke verkeersstromen wel en niet toegelaten zijn, kan BluePeak spreken van een enterprise-ready securityarchitectuur.
