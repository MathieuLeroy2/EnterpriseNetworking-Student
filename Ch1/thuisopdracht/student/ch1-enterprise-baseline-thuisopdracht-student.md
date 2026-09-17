# Thuisoefening 1 - Analyse van Asteria Logistics

## 1. Situering

Deze thuisoefening is een extra oefening bij hoofdstuk 1. Je krijgt een ander netwerk dan in de klassikale workshop.

Het doel blijft hetzelfde: je onderzoekt of een bestaand netwerk klaar is om uit te groeien tot een enterprise netwerk.

Je kijkt dus niet alleen naar de vraag:

> Werkt het netwerk technisch?

Je onderzoekt ook:

- Is het netwerk schaalbaar?
- Is het netwerk veilig?
- Is het netwerk betrouwbaar?
- Is het netwerk beheerbaar?
- Zijn zones logisch gescheiden?
- Zijn managementinterfaces voldoende beschermd?
- Is de documentatie duidelijk?

---

## 2. Scenario

Het bedrijf **Asteria Logistics** heeft een klein hoofdkantoor met een magazijn.

Het netwerk wordt gebruikt door:

- kantoorwerknemers;
- magazijnmedewerkers;
- gasten;
- IoT-toestellen zoals camera's en scanners;
- een interne ERP-server;
- netwerkbeheerders;
- externe partners.

De ERP-server bevat bedrijfsinformatie over bestellingen, voorraad en leveringen. Sommige externe partners moeten een webdienst kunnen bereiken.

Het bedrijf groeit en wil weten of het huidige netwerk professioneel genoeg is om verder op te bouwen.

Jouw opdracht:

> Analyseer het bestaande netwerk en bepaal of het enterprise-ready is.

---

## 3. Beginsituatie

Je krijgt een Packet Tracer-bestand met het netwerk van Asteria Logistics.

Het netwerk bevat:

- een router;
- twee switches;
- meerdere VLAN's;
- clients in verschillende zones;
- een interne server;
- een internet/ISP-server;
- DHCP;
- NAT/PAT;
- ACL's;
- managementinterfaces.

Het netwerk werkt op het eerste gezicht. Toch kunnen er ontwerp-, security- en beheerproblemen aanwezig zijn.

Pas in het begin niets aan. Analyseer eerst.

---

## 4. In te dienen

Lever een kort analyseverslag in met:

1. topologietekening;
2. VLAN-tabel;
3. IP-adresplan;
4. zoneschema;
5. overzicht van routing, DHCP en NAT/PAT;
6. ACL- en managementanalyse;
7. securityregelmatrix;
8. testplan met resultaten;
9. risico- en verbeterpuntenlijst;
10. conclusie.

---

## 5. Stap 1: topologie verkennen

Beantwoord:

- Welke netwerktoestellen zijn aanwezig?
- Welke clients en servers zijn aanwezig?
- Waar zit de internetverbinding?
- Welke verbindingen zijn trunks?
- Welke toestellen lijken kritisch?
- Zie je mogelijke single points of failure?

Maak een topologietekening.

Gebruik eventueel:

```text
show cdp neighbors
show ip interface brief
show interfaces trunk
```

Vul aan:

| Toestel | Rol | Belangrijke interfaces | Opmerking |
|---|---|---|---|
| ... | ... | ... | ... |

---

## 6. Stap 2: VLAN's onderzoeken

Gebruik:

```text
show vlan brief
show interfaces trunk
```

Beantwoord:

- Welke VLAN's bestaan er?
- Welke namen hebben ze?
- Welke poorten zitten in welk VLAN?
- Welke VLAN's gaan over de trunks?
- Wordt de native VLAN expliciet geconfigureerd?
- Zijn de VLAN's logisch gekoppeld aan functies of zones?

Vul in:

| VLAN | Naam | Poorten | Vermoedelijke functie | Opmerking |
|---:|---|---|---|---|
| ... | ... | ... | ... | ... |

---

## 7. Stap 3: IP-adresplan opstellen

Gebruik:

```text
show ip interface brief
show running-config
ipconfig
```

Beantwoord:

- Welk subnet hoort bij elk VLAN?
- Wat is de gateway per VLAN?
- Welke toestellen hebben een vast IP-adres?
- Welke toestellen krijgen DHCP?
- Zijn de subnetten logisch gekozen?
- Is er voldoende groeiruimte?

Vul in:

| VLAN | Subnet | Gateway | DHCP/statisch | Opmerking |
|---:|---|---|---|---|
| ... | ... | ... | ... | ... |

---

## 8. Stap 4: routing, DHCP en NAT/PAT analyseren

Gebruik:

```text
show ip route
show running-config
show ip nat translations
```

Beantwoord:

- Waar gebeurt inter-VLAN routing?
- Waar draaien de DHCP-pools?
- Waar gebeurt NAT/PAT?
- Is er een default route?
- Is er static NAT of port forwarding?
- Welke toestellen of interfaces zijn kritisch?

Vul in:

| Onderdeel | Locatie | Bewijs | Opmerking |
|---|---|---|---|
| Inter-VLAN routing | ... | ... | ... |
| DHCP | ... | ... | ... |
| NAT/PAT | ... | ... | ... |
| Default route | ... | ... | ... |
| Static NAT/port forwarding | ... | ... | ... |

---

## 9. Stap 5: zones bepalen

Bepaal welke zones aanwezig zijn.

Denk bijvoorbeeld aan:

- office;
- warehouse;
- guest;
- servers;
- IoT;
- management;
- internet.

Vul in:

| Zone | VLAN/subnet | Vertrouwensniveau | Waarom? |
|---|---|---|---|
| ... | ... | ... | ... |

Controleer vooral:

- Welke zones zijn laag vertrouwd?
- Welke zones bevatten kritieke systemen?
- Welke zones mogen zeker niet breed met elkaar communiceren?

---

## 10. Stap 6: ACL's en management onderzoeken

Gebruik:

```text
show access-lists
show running-config
```

Beantwoord:

- Welke ACL's bestaan er?
- Waar zijn ze toegepast?
- In welke richting zijn ze toegepast?
- Wat blokkeren ze?
- Wat laten ze toe?
- Zijn de ACL's volledig genoeg?
- Hoe is managementtoegang geconfigureerd?
- Is SSH aanwezig?
- Is managementtoegang beperkt tot beheerders?

Vul in:

| Onderdeel | Configuratie | Mogelijk risico | Opmerking |
|---|---|---|---|
| ACL | ... | ... | ... |
| VTY access | ... | ... | ... |
| SSH | ... | ... | ... |

---

## 11. Stap 7: securityregelmatrix maken

Maak een matrix van gewenst gedrag.

Vul in:

| Bronzone | Doelzone | Gewenst gedrag | Waarom? |
|---|---|---|---|
| Office | ERP server | ... | ... |
| Warehouse | ERP server | ... | ... |
| Guest | ERP server | ... | ... |
| Guest | Internet | ... | ... |
| IoT | ERP server | ... | ... |
| IoT | Management | ... | ... |
| Users | Management | ... | ... |
| Admin | Management | ... | ... |
| Internet | ERP server | ... | ... |

Vergelijk daarna je matrix met wat het netwerk echt doet.

---

## 12. Stap 8: gericht testen

Voer testen uit met een verwacht resultaat.

Vul in:

| Test | Verwacht resultaat | Werkelijk resultaat | Conclusie |
|---|---|---|---|
| Office naar ERP-server | ... | ... | ... |
| Warehouse naar ERP-server | ... | ... | ... |
| Guest naar internet | ... | ... | ... |
| Guest naar ERP-server | ... | ... | ... |
| Guest naar management-IP | ... | ... | ... |
| IoT naar ERP-server | ... | ... | ... |
| IoT naar management-IP | ... | ... | ... |
| Office naar management-IP | ... | ... | ... |
| Admin naar management-IP | ... | ... | ... |
| Externe server naar publieke webdienst | ... | ... | ... |

Belangrijk:

Test zowel verkeer dat moet werken als verkeer dat geblokkeerd zou moeten zijn.

---

## 13. Stap 9: risico's formuleren

Zoek minstens zes risico's.

Vul in:

| Risico | Impact | Bewijs of test | Mogelijke verbetering |
|---|---|---|---|
| ... | ... | ... | ... |

Denk aan:

- laag vertrouwde zones;
- managementtoegang;
- IoT;
- publieke toegang;
- schaalbaarheid;
- trunking;
- native VLAN;
- single points of failure;
- zwakke beheerconfiguratie.

---

## 14. Stap 10: verbeterpunten formuleren

Formuleer minstens zes concrete verbeterpunten.

Vul in:

| Verbeterpunt | Welk probleem lost dit op? | Hoe test je dit? |
|---|---|---|
| ... | ... | ... |

Maak verbeterpunten concreet.

Niet:

> Security verbeteren.

Wel:

> Blokkeer IoT-verkeer naar management en laat alleen noodzakelijke communicatie naar specifieke servers toe.

---

## 15. Conclusie

Schrijf een conclusie van 8 tot 12 regels.

Beantwoord:

- Wat werkt technisch goed?
- Welke risico's zijn het belangrijkst?
- Is het netwerk schaalbaar?
- Is het netwerk veilig genoeg?
- Is het netwerk beheerbaar?
- Welke verbeteringen hebben prioriteit?
- Is dit netwerk enterprise-ready?

Vermijd een conclusie zoals:

> Alles werkt.

Een goede conclusie maakt onderscheid tussen technisch werken en professioneel ontworpen zijn.
