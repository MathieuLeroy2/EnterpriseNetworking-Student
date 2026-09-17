# Workshop 1 - Analyse van een bestaand campusnetwerk

## 1. Situering

In het vorige OPO leerde je een netwerk technisch werkend maken. In deze workshop ga je een stap verder: je onderzoekt of een bestaand netwerk ook geschikt is als basis voor een enterprise netwerk.

Het netwerk dat je krijgt werkt op het eerste gezicht grotendeels correct. Dat betekent niet automatisch dat het netwerk goed ontworpen is.

Je opdracht is om het netwerk te analyseren als een junior netwerkbeheerder of consultant. Je zoekt niet alleen naar configuratiefouten, maar vooral naar ontwerpkeuzes die invloed hebben op:

- schaalbaarheid;
- betrouwbaarheid;
- security;
- beheerbaarheid;
- documentatie;
- troubleshooting.

Deze workshop is dus geen gewone configuratieoefening. Het doel is niet om meteen alles te herstellen, maar om het netwerk professioneel te beoordelen.

---

## 2. Scenario

Het bedrijf **NetNova** heeft vorig jaar een basisnetwerk laten installeren.

Het netwerk bevat onder andere:

- meerdere VLAN's;
- inter-VLAN routing;
- DHCP;
- NAT/PAT;
- internettoegang;
- een intern servernetwerk;
- een gastennetwerk;
- managementadressen voor netwerktoestellen;
- enkele ACL's.

Het bedrijf groeit. Er komen meer medewerkers, meer applicaties, bezoekers, externe partners en strengere securityvereisten.

De directie stelt daarom deze vraag:

> Is het huidige netwerk klaar om uit te groeien tot een enterprise netwerk?

Jullie worden gevraagd om een eerste technische analyse te maken.

---

## 3. Beginsituatie

Je krijgt een Packet Tracer-bestand van het bestaande netwerk.

Het netwerk is bewust niet perfect. Sommige onderdelen werken correct, andere onderdelen zijn onduidelijk, onveilig, moeilijk schaalbaar of onvoldoende gedocumenteerd.

Let op:

- Een succesvolle ping betekent niet automatisch dat het ontwerp goed is.
- Een ACL die bestaat, betekent niet automatisch dat het netwerk veilig is.
- Een VLAN dat technisch werkt, betekent niet automatisch dat het logisch gebruikt wordt.
- Een netwerk zonder duidelijke documentatie is moeilijk professioneel te beheren.

---

## 4. Doelen van de workshop

Na deze workshop kan je:

1. een bestaand Packet Tracer-netwerk methodisch verkennen;
2. VLAN's, subnetten, gateways en trunks terugvinden;
3. routing, DHCP, NAT/PAT en ACL's herkennen in een bestaande configuratie;
4. een fysieke en logische topologie maken;
5. netwerkzones herkennen en benoemen;
6. toegelaten en verboden verkeersstromen testen;
7. risico's benoemen rond security, schaalbaarheid, betrouwbaarheid en beheerbaarheid;
8. concrete verbeterpunten formuleren;
9. een korte conclusie schrijven over de enterprise-readiness van het netwerk.

---

## 5. Benodigdheden

Je hebt nodig:

- Cisco Packet Tracer;
- het Packet Tracer-bestand van NetNova;
- dit workshopdocument;
- het cursushoofdstuk over enterprise baseline en design;
- een tekstverwerker of Markdown-editor;
- eventueel papier of een digitaal tekenprogramma voor je topologie.

Je gebruikt voorkennis over:

- VLAN's;
- trunking;
- inter-VLAN routing;
- IP-adressering;
- DHCP;
- NAT/PAT;
- ACL's;
- `show`-commando's;
- `ping` en eventueel `traceroute`.

---

## 6. Werkwijze

Werk methodisch. Pas niet meteen configuraties aan.

Je analyse verloopt in deze volgorde:

1. topologie verkennen;
2. VLAN's en subnetten documenteren;
3. routing, DHCP en NAT/PAT onderzoeken;
4. zones en toegangsregels analyseren;
5. gerichte testen uitvoeren;
6. risico's en verbeterpunten formuleren;
7. conclusie schrijven.

---

## 7. Stap 1: verken de topologie

Open het Packet Tracer-bestand en bekijk eerst de topologie.

Beantwoord:

- Welke routers zijn aanwezig?
- Welke switches zijn aanwezig?
- Welke clients zijn aanwezig?
- Welke servers zijn aanwezig?
- Waar lijkt de internetverbinding te zitten?
- Welke toestellen lijken centraal of kritisch?
- Zijn er verbindingen die een single point of failure kunnen vormen?

Maak een eerste ruwe topologietekening.

Je tekening moet minstens tonen:

- toestelnamen;
- verbindingen tussen toestellen;
- belangrijke poorten of uplinks;
- serverlocatie;
- internet- of ISP-verbinding;
- waar mogelijk: VLAN's of zones.

Controlepunt:

> Kan iemand anders aan de hand van je tekening begrijpen hoe het netwerk fysiek in elkaar zit?

---

## 8. Stap 2: breng VLAN's in kaart

Onderzoek welke VLAN's bestaan en waar ze gebruikt worden.

Gebruik bijvoorbeeld:

```text
show vlan brief
show interfaces trunk
```

Beantwoord:

- Welke VLAN's bestaan er?
- Welke naam heeft elk VLAN?
- Welke accesspoorten horen bij welk VLAN?
- Welke trunkpoorten bestaan er?
- Welke VLAN's mogen over de trunks?
- Wordt de native VLAN expliciet vermeld?
- Zijn er VLAN's die onduidelijk of slecht benoemd zijn?

Vul deze tabel in:

| VLAN | Naam | Gebruikte poorten | Doel | Opmerking |
|---:|---|---|---|---|
| ... | ... | ... | ... | ... |

Controlepunt:

> Komt het gebruik van elk VLAN overeen met de naam en het doel ervan?

---

## 9. Stap 3: maak een IP-adresplan

Onderzoek welke IP-subnetten gebruikt worden.

Gebruik bijvoorbeeld:

```text
show ip interface brief
show running-config
```

Beantwoord:

- Welk subnet hoort bij welk VLAN?
- Wat is de default gateway per VLAN?
- Welke toestellen hebben een vast IP-adres?
- Welke toestellen krijgen een IP-adres via DHCP?
- Zijn de IP-ranges logisch gekozen?
- Is er ruimte voor groei?

Vul deze tabel in:

| VLAN | Subnet | Gateway | DHCP of statisch? | Opmerking |
|---:|---|---|---|---|
| ... | ... | ... | ... | ... |

Controlepunt:

> Kan je voor elke client uitleggen waarom die in dat subnet zit?

---

## 10. Stap 4: onderzoek routing, DHCP en NAT/PAT

Onderzoek hoe verkeer tussen VLAN's en naar internet loopt.

Gebruik bijvoorbeeld:

```text
show ip interface brief
show ip route
show running-config
show ip nat translations
```

Beantwoord:

- Waar gebeurt inter-VLAN routing?
- Welk toestel is default gateway voor de VLAN's?
- Waar staan de DHCP-pools?
- Waar gebeurt NAT/PAT?
- Is er een default route naar internet?
- Welke interface is de inside-kant van NAT?
- Welke interface is de outside-kant van NAT?
- Is een enkel toestel kritisch voor routing en internettoegang?

Vul deze tabel in:

| Onderdeel | Waar gebeurt dit? | Bewijs of commando | Opmerking |
|---|---|---|---|
| Inter-VLAN routing | ... | ... | ... |
| DHCP | ... | ... | ... |
| NAT/PAT | ... | ... | ... |
| Default route | ... | ... | ... |

Controlepunt:

> Kan je het pad uitleggen van een client naar de interne server en van een client naar internet?

---

## 11. Stap 5: bepaal de netwerkzones

Vertaal de VLAN's en subnetten naar zones.

Denk aan mogelijke zones zoals:

- internal users;
- staff;
- guests;
- servers;
- management;
- internet.

Beantwoord:

- Welke zones herken je?
- Welke VLAN's horen bij welke zone?
- Welke zones vertrouw je weinig?
- Welke zones zijn kritisch?
- Welke zones mogen zeker niet zomaar met elkaar communiceren?

Vul deze tabel in:

| Zone | VLAN's of subnetten | Vertrouwensniveau | Waarom? |
|---|---|---|---|
| ... | ... | ... | ... |

Controlepunt:

> Zijn alle interne zones even betrouwbaar, of moet je daar onderscheid in maken?

---

## 12. Stap 6: analyseer ACL's en toegangsregels

Onderzoek welke ACL's bestaan en waar ze toegepast zijn.

Gebruik bijvoorbeeld:

```text
show access-lists
show running-config
```

Beantwoord:

- Welke ACL's bestaan er?
- Wat probeert elke ACL te doen?
- Waar is elke ACL toegepast?
- In welke richting is elke ACL toegepast?
- Welke verkeersstromen worden toegestaan?
- Welke verkeersstromen worden geblokkeerd?
- Zijn er regels die te breed zijn?
- Zijn er zones die onvoldoende beschermd zijn?

Vul deze tabel in:

| ACL | Toegepast op | Richting | Bedoeling | Mogelijk probleem |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

Controlepunt:

> Is het verschil duidelijk tussen een ACL die bestaat en een ACL die effectief correct toegepast is?

---

## 13. Stap 7: maak een securityregelmatrix

Maak nu zelf een overzicht van welke zones met elkaar mogen communiceren.

Begin met wat volgens jou logisch zou zijn in een enterprise netwerk.

Vul deze tabel in:

| Bronzone | Doelzone | Gewenst gedrag | Waarom? |
|---|---|---|---|
| Staff | Servers | ... | ... |
| Guests | Internet | ... | ... |
| Guests | Servers | ... | ... |
| Users | Management | ... | ... |
| IT of Management | Management | ... | ... |
| Internet | Internal users | ... | ... |

Daarna vergelijk je dit gewenste gedrag met wat het netwerk echt doet.

Controlepunt:

> Waar wijkt het echte netwerk af van wat je als goed enterprise-ontwerp zou verwachten?

---

## 14. Stap 8: voer gerichte testen uit

Test niet willekeurig. Elke test moet een verwacht resultaat hebben.

Gebruik bijvoorbeeld:

- `ping`;
- webbrowser naar een server;
- eventueel `traceroute`;
- eventueel SSH of Telnet-testen als dit in Packet Tracer beschikbaar is.

Vul deze tabel in:

| Test | Verwacht resultaat | Werkelijk resultaat | Conclusie |
|---|---|---|---|
| Client naar eigen gateway | ... | ... | ... |
| Staff naar interne server | ... | ... | ... |
| Guest naar internet | ... | ... | ... |
| Guest naar interne server | ... | ... | ... |
| Student naar management-IP | ... | ... | ... |
| IT naar management-IP | ... | ... | ... |
| Internetserver naar interne client | ... | ... | ... |

Belangrijk:

> Test ook verkeer dat niet zou mogen werken.

Een test waarbij verboden verkeer correct geblokkeerd wordt, is even belangrijk als een test waarbij toegelaten verkeer werkt.

Controlepunt:

> Heb je zowel toegelaten als verboden verkeersstromen getest?

---

## 15. Stap 9: formuleer risico's

Maak een lijst van risico's die je hebt gevonden.

Een goed risico is concreet.

Niet:

> Security is slecht.

Wel:

> Het guest VLAN kan een interne server bereiken. Daardoor kunnen onbekende toestellen interne systemen scannen of aanvallen.

Vul deze tabel in:

| Risico | Impact | Bewijs of test | Mogelijke verbetering |
|---|---|---|---|
| ... | ... | ... | ... |

Zoek minstens vijf risico's of tekortkomingen.

Denk aan:

- security;
- schaalbaarheid;
- betrouwbaarheid;
- beheerbaarheid;
- documentatie;
- managementtoegang;
- guest access;
- trunkconfiguratie;
- single points of failure.

Controlepunt:

> Kan je bij elk risico uitleggen waarom het belangrijk is?

---

## 16. Stap 10: formuleer verbeterpunten

Formuleer nu concrete verbeterpunten.

Een verbetering moet toetsbaar zijn.

Niet:

> Maak het netwerk veiliger.

Wel:

> Blokkeer verkeer van het guest VLAN naar interne subnetten, maar laat verkeer naar internet toe.

Vul deze tabel in:

| Verbeterpunt | Welk probleem lost dit op? | Hoe kan je dit testen? |
|---|---|---|
| ... | ... | ... |

Zoek minstens vijf concrete verbeterpunten.

Controlepunt:

> Kan je achteraf testen of het verbeterpunt echt werkt?

---

## 17. Stap 11: schrijf je conclusie

Beantwoord de centrale vraag:

> Is het netwerk van NetNova klaar om uit te groeien tot een enterprise netwerk?

Schrijf een korte conclusie van 8 tot 12 regels.

Je conclusie bevat:

- wat technisch goed werkt;
- welke belangrijke risico's je vond;
- welke risico's prioriteit hebben;
- welke verbeteringen je eerst zou uitvoeren;
- waarom het netwerk wel of niet enterprise-ready is.

Gebruik geen vage conclusie zoals:

> Alles werkt.

Een goede conclusie maakt onderscheid tussen:

- technisch werkend;
- veilig;
- schaalbaar;
- betrouwbaar;
- beheerbaar.

---

## 18. In te dienen

Lever een kort analyseverslag in.

Je verslag bevat minstens:

1. topologietekening;
2. VLAN-tabel;
3. IP-adresplan;
4. zoneschema;
5. overzicht van routing, DHCP en NAT/PAT;
6. ACL-analyse;
7. securityregelmatrix;
8. testplan met resultaten;
9. risico- en verbeterpuntenlijst;
10. korte conclusie.

Het verslag hoeft niet lang te zijn. Het moet wel duidelijk en controleerbaar zijn.

---

## 19. Typische valkuilen

Let op voor deze fouten:

| Valkuil | Waarom is dit een probleem? |
|---|---|
| Alleen testen of ping werkt | Je test dan niet of verkeer ook terecht toegelaten is |
| Alleen kijken naar configuratie | Je weet dan niet of de configuratie het gewenste effect heeft |
| ACL's zien en aannemen dat security ok is | Een ACL kan onvolledig of verkeerd toegepast zijn |
| Managementtoegang vergeten | Beheerinterfaces zijn vaak kritieke doelwitten |
| Guest access onderschatten | Gasttoestellen zijn niet beheerd door de organisatie |
| Geen onderscheid maken tussen VLAN en zone | VLAN's zijn technisch, zones gaan over functie en vertrouwen |
| Geen testresultaten noteren | Je analyse is dan moeilijk controleerbaar |
| Vage verbeteringen formuleren | Je kan ze niet uitvoeren of testen |

---

## 20. Hulpvragen

Gebruik deze vragen als je vastloopt:

- Welk VLAN gebruikt deze client?
- Heeft de client een correct IP-adres?
- Wat is de default gateway?
- Bestaat het VLAN op de juiste switch?
- Mag het VLAN over de trunk?
- Waar gebeurt routing?
- Bestaat er een route naar het doelnetwerk?
- Is NAT nodig voor deze verkeersstroom?
- Bestaat er een ACL die dit verkeer kan blokkeren?
- Is de ACL op de juiste interface en richting toegepast?
- Is dit verkeer gewenst vanuit enterprise-standpunt?
- Is dit een technisch probleem of een ontwerprisico?

---

## 21. Eindvraag

Sluit je verslag af met een antwoord op deze vraag:

> Wat is het belangrijkste verschil tussen een netwerk dat technisch werkt en een netwerk dat professioneel beheerd kan worden?

