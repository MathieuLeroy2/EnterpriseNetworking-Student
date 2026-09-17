# Workshop 1 - Modeloplossing voor studenten

## 1. Doel van deze modeloplossing

Dit document toont een mogelijke oplossing voor **Workshop 1 - Analyse van een bestaand campusnetwerk**.

De bedoeling is niet dat elke formulering exact hetzelfde is als in jouw verslag. Een goede oplossing moet wel dezelfde kern bevatten:

- een correcte analyse van VLAN's en subnetten;
- een overzicht van routing, DHCP, NAT/PAT en ACL's;
- een zoneschema;
- gerichte testresultaten;
- concrete risico's;
- duidelijke verbeterpunten;
- een onderbouwde conclusie over de enterprise-readiness van het netwerk.

---

## 2. Korte samenvatting van het netwerk

Het netwerk van NetNova bestaat uit:

- een edge-router: `R1-EDGE`;
- een core switch: `SW1-CORE`;
- een access switch: `SW2-ACCESS`;
- meerdere VLAN's;
- router-on-a-stick voor inter-VLAN routing;
- DHCP op de router;
- NAT/PAT op de router voor internettoegang;
- een interne server;
- een gesimuleerde internetserver;
- managementinterfaces op de switches;
- een ACL voor het guest VLAN.

Het netwerk werkt technisch voor basisconnectiviteit, maar bevat meerdere ontwerp- en securityproblemen.

---

## 3. Topologie

Een correcte topologietekening moet minstens deze structuur tonen:

| Van | Naar | Verbinding | Functie |
|---|---|---|---|
| `R1-EDGE G0/0` | `SW1-CORE G0/1` | trunk | router-on-a-stick |
| `R1-EDGE G0/1` | `ISP-SERVER Fa0` | routed link | internet/ISP-simulatie |
| `SW1-CORE G0/2` | `SW2-ACCESS G0/1` | trunk | verbinding core-access |
| `SW1-CORE Fa0/1` | `SRV-INTERNAL Fa0` | accesspoort | interne server |
| `SW2-ACCESS Fa0/1` | `PC-STUDENT Fa0` | accesspoort | studentennetwerk |
| `SW2-ACCESS Fa0/2` | `PC-STAFF Fa0` | accesspoort | medewerkersnetwerk |
| `SW2-ACCESS Fa0/3` | `PC-GUEST Fa0` | accesspoort | gastennetwerk |
| `SW2-ACCESS Fa0/4` | `PC-IT Fa0` | accesspoort | management/IT |

Belangrijke vaststelling:

`R1-EDGE` is een kritisch toestel. Het verzorgt inter-VLAN routing, DHCP, NAT/PAT en internettoegang. Als dit toestel uitvalt, heeft dat impact op bijna het volledige netwerk.

---

## 4. VLAN-tabel

| VLAN | Naam | Gebruikte poorten | Doel | Opmerking |
|---:|---|---|---|---|
| 10 | `STUDENTS` | `SW2 Fa0/1` | studententoestellen | logisch gescheiden clientgroep |
| 20 | `STAFF` | `SW2 Fa0/2` | medewerkers | interne gebruikers |
| 30 | `SERVERS` | `SW1 Fa0/1` | interne server | bevat kritieke dienst |
| 40 | `GUESTS` | `SW2 Fa0/3` | bezoekers | laag vertrouwd |
| 99 | `MGMT` | `SW2 Fa0/4`, SVI's switches | management | kritisch, moet beperkt bereikbaar zijn |

Trunks:

| Switch | Poort | Verbinding | Vaststelling |
|---|---|---|---|
| `SW1-CORE` | `G0/1` | naar `R1-EDGE` | trunk |
| `SW1-CORE` | `G0/2` | naar `SW2-ACCESS` | trunk |
| `SW2-ACCESS` | `G0/1` | naar `SW1-CORE` | trunk |

Belangrijke vaststelling:

De trunks laten alle VLAN's toe. Dat werkt technisch, maar is niet ideaal. In een enterprise netwerk beperk je trunklinks bij voorkeur tot de VLAN's die daar echt nodig zijn.

Daarnaast blijft de native VLAN standaard VLAN 1. Dat is een zwakkere standaardconfiguratie en wordt best vervangen door een ongebruikte native VLAN.

---

## 5. IP-adresplan

| VLAN | Subnet | Gateway | DHCP of statisch? | Opmerking |
|---:|---|---|---|---|
| 10 | `10.10.10.0/24` | `10.10.10.1` | DHCP | students |
| 20 | `10.10.20.0/24` | `10.10.20.1` | DHCP | staff |
| 30 | `10.10.30.0/24` | `10.10.30.1` | statisch | servers |
| 40 | `10.10.40.0/24` | `10.10.40.1` | DHCP | guests |
| 99 | `10.10.99.0/24` | `10.10.99.1` | DHCP en statisch | management |

Vaste adressen:

| Toestel | IP-adres | Functie |
|---|---|---|
| `SRV-INTERNAL` | `10.10.30.10` | interne server |
| `SW1-CORE` | `10.10.99.11` | management-IP |
| `SW2-ACCESS` | `10.10.99.12` | management-IP |
| `R1-EDGE G0/1` | `203.0.113.9` | ISP-link |
| `ISP-SERVER` | `203.0.113.10` | internetserver |

Belangrijke vaststelling:

Het IP-plan is bruikbaar voor een labo, maar moet beter gedocumenteerd worden voor een enterprise omgeving. Vooral het managementnetwerk vraagt duidelijke afspraken over vaste adressen, toegangsrechten en beheer.

---

## 6. Routing, DHCP en NAT/PAT

| Onderdeel | Waar gebeurt dit? | Bewijs of commando | Opmerking |
|---|---|---|---|
| Inter-VLAN routing | `R1-EDGE` | `show ip interface brief` | subinterfaces `G0/0.10`, `.20`, `.30`, `.40`, `.99` |
| DHCP | `R1-EDGE` | `show running-config` | DHCP-pools per VLAN |
| NAT/PAT | `R1-EDGE` | `show running-config`, `show ip nat translations` | overload op `G0/1` |
| Default route | `R1-EDGE` | `show ip route` | route naar `203.0.113.10` |
| Internet/ISP | `ISP-SERVER` | ping of webtest | simuleert externe server |

Belangrijke vaststelling:

`R1-EDGE` is een single point of failure. Het toestel verzorgt te veel kritieke functies tegelijk:

- routing tussen VLAN's;
- DHCP;
- NAT/PAT;
- internettoegang;
- filtering voor het guest VLAN.

Als `R1-EDGE` uitvalt, verliezen clients hun inter-VLAN connectiviteit en internettoegang.

---

## 7. Zoneschema

| Zone | VLAN's of subnetten | Vertrouwensniveau | Waarom? |
|---|---|---|---|
| Students | VLAN 10, `10.10.10.0/24` | gemiddeld | gekende gebruikers, maar geen beheerders |
| Staff | VLAN 20, `10.10.20.0/24` | gemiddeld tot hoog | medewerkers met toegang tot bedrijfsdiensten |
| Servers | VLAN 30, `10.10.30.0/24` | hoog | bevat interne applicaties of data |
| Guests | VLAN 40, `10.10.40.0/24` | laag | toestellen zijn niet beheerd door NetNova |
| Management | VLAN 99, `10.10.99.0/24` | zeer hoog | beheer van switches en router |
| Internet | `203.0.113.8/30` en verder | zeer laag | externe omgeving |

Belangrijke vaststelling:

Niet alle interne netwerken zijn even betrouwbaar. Vooral `GUESTS` en `MGMT` moeten veel strikter gescheiden worden.

---

## 8. ACL-analyse

Er is een extended ACL aanwezig voor het guest VLAN.

Relevante ACL:

```text
ip access-list extended GUEST_LIMITED
 permit udp any eq bootpc any eq bootps
 deny ip 10.10.40.0 0.0.0.255 10.10.99.0 0.0.0.255
 permit ip 10.10.40.0 0.0.0.255 any
```

De ACL is toegepast op:

```text
interface g0/0.40
 ip access-group GUEST_LIMITED in
```

Analyse:

| ACL | Toegepast op | Richting | Bedoeling | Mogelijk probleem |
|---|---|---|---|---|
| `GUEST_LIMITED` | `R1-EDGE G0/0.40` | inbound | guest beperken naar management | guest naar servernetwerk blijft toegelaten |

Wat doet de ACL wel?

- DHCP voor guests blijft mogelijk.
- Guest-verkeer naar het managementnetwerk `10.10.99.0/24` wordt geblokkeerd.
- Guest-verkeer naar internet wordt toegelaten.

Wat doet de ACL niet?

- Guest-verkeer naar het servernetwerk `10.10.30.0/24` wordt niet geblokkeerd.
- Guest-verkeer naar andere interne subnetten, behalve management, blijft mogelijk.

Belangrijke conclusie:

De ACL bestaat, maar is onvolledig. Het bestaan van een ACL betekent dus niet automatisch dat het securitybeleid correct is.

---

## 9. Securityregelmatrix

Een gewenste enterprise-regelmatrix kan er zo uitzien:

| Bronzone | Doelzone | Gewenst gedrag | Waarom? |
|---|---|---|---|
| Students | Internet | toegelaten | studenten hebben internettoegang nodig |
| Staff | Internet | toegelaten | medewerkers hebben internettoegang nodig |
| Guests | Internet | toegelaten | bezoekers mogen internet gebruiken |
| Staff | Servers | toegelaten | medewerkers gebruiken interne applicaties |
| Students | Servers | beperkt of afhankelijk van toepassing | niet elke studentendienst mag alle servers bereiken |
| Guests | Servers | geblokkeerd | guests zijn laag vertrouwd |
| Students | Management | geblokkeerd | studenten beheren geen netwerktoestellen |
| Staff | Management | geblokkeerd, tenzij IT | gewone medewerkers beheren geen netwerktoestellen |
| IT/Mgmt | Management | toegelaten | beheerders moeten toestellen kunnen beheren |
| Internet | Internal users | geblokkeerd | interne clients mogen niet rechtstreeks van buiten bereikbaar zijn |

Afwijkingen in het huidige netwerk:

| Afwijking | Waarom problematisch? |
|---|---|
| Guests kunnen de interne server bereiken | laag vertrouwde toestellen krijgen toegang tot intern systeem |
| Students kunnen management-IP's bereiken | gewone clients kunnen beheerinterfaces scannen |
| Staff kunnen management-IP's bereiken | toegang is breder dan nodig |
| Trunks laten alle VLAN's toe | VLAN's worden onnodig verspreid |
| Telnet is toegelaten | beheerprotocol is onveilig |

---

## 10. Testplan met resultaten

Een mogelijk testplan:

| Test | Verwacht vanuit enterprise-standpunt | Werkelijk resultaat | Conclusie |
|---|---|---|---|
| `PC-STUDENT` naar eigen gateway `10.10.10.1` | werkt | werkt | VLAN 10 gateway bereikbaar |
| `PC-STAFF` naar eigen gateway `10.10.20.1` | werkt | werkt | VLAN 20 gateway bereikbaar |
| `PC-GUEST` naar eigen gateway `10.10.40.1` | werkt | werkt | VLAN 40 gateway bereikbaar |
| `PC-STUDENT` naar `SRV-INTERNAL 10.10.30.10` | afhankelijk van beleid | werkt | studentennetwerk kan server bereiken |
| `PC-STAFF` naar `SRV-INTERNAL 10.10.30.10` | werkt | werkt | staff kan server bereiken |
| `PC-GUEST` naar `SRV-INTERNAL 10.10.30.10` | werkt niet | werkt | securityprobleem |
| `PC-GUEST` naar `SW1-CORE 10.10.99.11` | werkt niet | werkt niet | ACL blokkeert guest naar management |
| `PC-STUDENT` naar `SW1-CORE 10.10.99.11` | werkt niet | werkt | securityprobleem |
| `PC-STAFF` naar `SW2-ACCESS 10.10.99.12` | werkt niet, tenzij IT | werkt | securityprobleem |
| `PC-GUEST` naar `ISP-SERVER 203.0.113.10` | werkt | werkt | guest heeft internettoegang |
| `PC-STUDENT` naar `ISP-SERVER 203.0.113.10` | werkt | werkt | internettoegang werkt |

Belangrijke vaststelling:

Het netwerk werkt technisch, maar sommige succesvolle testen zijn net een probleem. Vooral `PC-GUEST` naar de interne server en gewone clients naar management-IP's tonen aan dat de segmentatie onvoldoende streng is.

---

## 11. Risico- en verbeterpuntenlijst

| Risico | Impact | Bewijs of test | Mogelijke verbetering |
|---|---|---|---|
| Guest VLAN kan interne server bereiken | hoog | `PC-GUEST` kan `10.10.30.10` bereiken | blokkeer guest naar interne subnetten |
| Students kunnen management-IP's bereiken | hoog | `PC-STUDENT` kan `10.10.99.11` bereiken | beperk management tot IT of managementzone |
| Staff kunnen management-IP's bereiken | hoog | `PC-STAFF` kan `10.10.99.12` bereiken | gebruik ACL of VTY access-class |
| Telnet is toegelaten | hoog | `transport input ssh telnet` | laat alleen SSH toe |
| Zwakke didactische wachtwoorden | hoog | `Cisco123`, `class` | gebruik sterk wachtwoordbeleid |
| Trunks laten alle VLAN's toe | middel | `show interfaces trunk` | beperk allowed VLAN's |
| Native VLAN blijft VLAN 1 | middel | trunkconfiguratie | gebruik ongebruikte native VLAN |
| Router is single point of failure | hoog | alle gateways en NAT op `R1-EDGE` | redundantie voorzien |
| ACL is onvolledig | hoog | guest naar servers blijft toegelaten | ACL baseren op securityregelmatrix |
| Geen DMZ | middel | interne server staat in intern servernetwerk | publieke diensten in DMZ plaatsen |
| Geen monitoring of logging | middel | geen voorziening zichtbaar | monitoring en centrale logging toevoegen |
| Beperkte documentatie | middel | analyse vereist veel opzoekwerk | VLAN-, IP-, zone- en ACL-documentatie bijhouden |

---

## 12. Concrete verbeterpunten

| Verbeterpunt | Welk probleem lost dit op? | Hoe kan je dit testen? |
|---|---|---|
| Blokkeer guest naar alle interne `10.10.0.0/16`-subnetten | guests kunnen interne systemen bereiken | `PC-GUEST` naar `10.10.30.10` moet falen |
| Laat guest alleen naar internet toe | beperkt laag vertrouwde toestellen | `PC-GUEST` naar `203.0.113.10` moet blijven werken |
| Beperk managementtoegang tot VLAN 99 of IT-beheerders | gewone clients kunnen management-IP's bereiken | `PC-STUDENT` naar `10.10.99.11` moet falen, `PC-IT` moet werken |
| Schakel Telnet uit en gebruik alleen SSH | Telnet is onveilig | VTY-configuratie toont alleen `transport input ssh` |
| Gebruik sterke wachtwoorden | didactische wachtwoorden zijn zwak | controleer configuratiebeleid |
| Beperk allowed VLAN's op trunks | VLAN's worden onnodig verspreid | `show interfaces trunk` toont alleen nodige VLAN's |
| Stel een ongebruikte native VLAN in | VLAN 1 blijft standaard/native | trunkconfiguratie toont bijvoorbeeld native VLAN 999 |
| Voorzie redundantie voor kritieke functies | router/uplink is single point of failure | ontwerp bevat tweede pad of failoverconcept |
| Maak een securityregelmatrix | ACL's zijn niet gekoppeld aan beleid | elke ACL kan aan een requirement gekoppeld worden |
| Documenteer VLAN's, IP-plan en zones | netwerk is moeilijk beheerbaar | analyse kan gelezen worden zonder Packet Tracer te openen |

---

## 13. Mogelijke verbeterde ACL voor guest VLAN

Een betere guest-ACL blokkeert guests naar interne subnetten, maar laat internettoegang toe.

Voorbeeld:

```text
configure terminal
no ip access-list extended GUEST_LIMITED

ip access-list extended GUEST_LIMITED
 remark Guests may not access internal private networks
 permit udp any eq bootpc any eq bootps
 deny ip 10.10.40.0 0.0.0.255 10.10.0.0 0.0.255.255
 permit ip 10.10.40.0 0.0.0.255 any
exit

interface g0/0.40
 ip access-group GUEST_LIMITED in
end
```

Verwacht effect:

| Test | Verwacht na verbetering |
|---|---|
| `PC-GUEST` naar `10.10.30.10` | werkt niet |
| `PC-GUEST` naar `10.10.99.11` | werkt niet |
| `PC-GUEST` naar `203.0.113.10` | werkt |
| `PC-GUEST` DHCP | blijft werken |

Let op:

De DHCP-regel is nodig omdat DHCP Discover-verkeer vertrekt vanaf `0.0.0.0` naar broadcast. Zonder die regel kan de guest-client mogelijk geen IP-adres krijgen.

---

## 14. Mogelijke beperking van managementtoegang

Een eenvoudige manier om VTY-toegang te beperken is een standard ACL met `access-class`.

Voorbeeld:

```text
configure terminal
ip access-list standard MGMT_ONLY
 permit 10.10.99.0 0.0.0.255
 deny any
exit

line vty 0 4
 access-class MGMT_ONLY in
 transport input ssh
exit
end
```

Dit moet worden toegepast op de toestellen waarop je managementtoegang wil beperken, bijvoorbeeld:

- `R1-EDGE`;
- `SW1-CORE`;
- `SW2-ACCESS`.

Verwacht effect:

| Test | Verwacht na verbetering |
|---|---|
| `PC-STUDENT` naar managementtoestel via VTY | werkt niet |
| `PC-STAFF` naar managementtoestel via VTY | werkt niet |
| `PC-GUEST` naar managementtoestel via VTY | werkt niet |
| `PC-IT` naar managementtoestel via VTY | werkt |

Belangrijk:

Dit beperkt VTY-loginverkeer. Het is geen volledige firewalloplossing voor alle mogelijke managementprotocollen, maar het is wel een duidelijke verbetering tegenover brede toegang.

---

## 15. Mogelijke trunkverbetering

Een trunk moet bij voorkeur alleen VLAN's vervoeren die nodig zijn.

Voorbeeld:

```text
configure terminal
vlan 999
 name UNUSED_NATIVE
exit

interface g0/1
 switchport trunk allowed vlan 10,20,30,40,99
 switchport trunk native vlan 999
exit
end
```

Pas dit consequent toe op beide kanten van een trunk.

Waarom is dit beter?

- VLAN's worden minder breed verspreid.
- De native VLAN is niet langer VLAN 1.
- De trunkconfiguratie is explicieter.
- Troubleshooting en securitycontrole worden duidelijker.

---

## 16. Modelconclusie

Het netwerk van NetNova werkt technisch voor basisconnectiviteit. Clients krijgen een IP-adres via DHCP, inter-VLAN routing werkt, de interne server is bereikbaar en clients kunnen via NAT/PAT naar de internetserver.

Toch is het netwerk nog niet klaar als enterprise netwerk. De belangrijkste problemen zitten in security, beheerbaarheid en betrouwbaarheid. Het guest VLAN kan de interne server bereiken, gewone client-VLAN's kunnen managementadressen bereiken en Telnet is nog toegelaten. Daarnaast zijn de trunks te breed geconfigureerd, blijft de native VLAN op VLAN 1 en is `R1-EDGE` een single point of failure voor routing, DHCP, NAT en internettoegang.

De eerste prioriteit is het beperken van toegang tussen zones. Guests mogen alleen naar internet, managementtoegang moet beperkt worden tot IT of de managementzone, en ACL's moeten gekoppeld worden aan een duidelijke securityregelmatrix. Daarna moeten trunkconfiguratie, documentatie, monitoring en redundantie verbeterd worden.

Conclusie: het netwerk is technisch werkend, maar nog niet enterprise-ready. Het mist een sterker securitymodel, betere afscherming van managementtoegang, duidelijkere documentatie en maatregelen tegen single points of failure.

---

## 17. Antwoord op de eindvraag

Het belangrijkste verschil tussen een technisch werkend netwerk en een professioneel beheerd netwerk is dat een professioneel netwerk niet alleen verbinding voorziet, maar ook bewust ontworpen, beveiligd, gedocumenteerd, getest en beheerbaar is.

In een technisch werkend netwerk kijk je vooral of verkeer mogelijk is. In een professioneel netwerk kijk je ook of dat verkeer gewenst, veilig, schaalbaar en controleerbaar is.

