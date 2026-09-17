# Workshop 3 - Security zoning en DMZ-design

## 1. Situering

In deze workshop ontwerp en analyseer je de securityarchitectuur van een bedrijfsnetwerk.

Je vertrekt niet van de vraag:

> Welke ACL moet ik typen?

Je vertrekt van de vraag:

> Welke zones bestaan er, welke zones vertrouwen we wel of niet, en welke communicatie is echt nodig?

Daarna vertaal je dat ontwerp naar een firewallregelmatrix en een testplan. Waar de Packet Tracer-omgeving dit toelaat, kan je bestaande ACL's analyseren of beperkte regels voorstellen. De nadruk ligt op security-denken, niet op syntax van nul.

---

## 2. Scenario

Het bedrijf **BluePeak Services** levert IT-diensten aan kleine organisaties. Het bedrijf groeit en wil zijn netwerk professioneler beveiligen.

BluePeak heeft:

- gewone medewerkers;
- een finance-afdeling;
- IT-beheerders;
- interne servers;
- een gastennetwerk;
- IoT-toestellen zoals camera's en printers;
- managementinterfaces van switches en routers;
- een publieke webdienst die bereikbaar moet zijn vanaf internet.

De huidige configuratie is gegroeid vanuit losse aanpassingen. Veel verkeer werkt, maar niemand weet zeker of dat verkeer ook gewenst is.

De directie stelt deze vraag:

> Kunnen jullie een duidelijk securitymodel ontwerpen met zones, een DMZ en least privilege-regels?

---

## 3. Beginsituatie

Je krijgt een Packet Tracer-bestand of een netwerkschema van BluePeak Services.

Het netwerk bevat verschillende VLAN's en subnetten. Sommige regels zijn bewust te breed, onduidelijk of slecht geplaatst.

Belangrijk:

- Een werkende ping is niet automatisch een goed resultaat.
- Een bestaande ACL betekent niet automatisch dat het beleid correct is.
- Een apart VLAN is geen volledige beveiliging als er geen filtering gebeurt.
- Een publieke server hoort niet zomaar in het interne servernetwerk.
- Managementtoegang moet strenger bekeken worden dan gewone applicatietoegang.

Pas niet meteen configuraties aan. Analyseer eerst.

---

## 4. Doelen

Na deze workshop kan je:

1. VLAN's en subnetten vertalen naar securityzones;
2. vertrouwensniveaus toekennen aan zones;
3. trust boundaries aanduiden in een netwerk;
4. bepalen welke diensten in een DMZ thuishoren;
5. een firewallregelmatrix opstellen volgens least privilege;
6. onderscheid maken tussen north-south en east-west traffic;
7. bestaande ACL's of firewallregels beoordelen vanuit beleid;
8. een testplan maken voor toegelaten en verboden verkeersstromen;
9. risico's formuleren rond te brede toegang;
10. een korte securityarchitectuurconclusie schrijven.

---

## 5. Benodigdheden

Je hebt nodig:

- Cisco Packet Tracer;
- het Packet Tracer-bestand of schema van BluePeak Services;
- dit workshopdocument;
- het cursushoofdstuk **Security architecture**;
- een tekstverwerker of Markdown-editor;
- eventueel een digitaal tekenprogramma voor je zoneschema.

Je gebruikt voorkennis over:

- VLAN's en subnetten;
- inter-VLAN routing;
- ACL's;
- NAT/PAT;
- `show`-commando's;
- `ping`, browser- en connectiviteitstesten.

---

## 6. Werkwijze

Gebruik deze volgorde:

1. topologie verkennen;
2. VLAN's en subnetten documenteren;
3. zones en vertrouwensniveaus bepalen;
4. trust boundaries aanduiden;
5. DMZ-ontwerp beoordelen of maken;
6. huidige toegangsregels analyseren;
7. firewallregelmatrix opstellen;
8. testplan uitvoeren of voorbereiden;
9. risico's en verbeterpunten formuleren;
10. eindconclusie schrijven.

---

## 7. Stap 1: verken de topologie

Open het Packet Tracer-bestand of bekijk het schema.

Beantwoord:

- Welke routers, switches en servers zijn aanwezig?
- Waar zit de internetverbinding?
- Waar staat de publieke webdienst?
- Waar staan de interne servers?
- Waar zitten gewone clients, finance, IT, guests en IoT?
- Waar gebeuren routing en filtering?
- Is er een duidelijke DMZ?

Maak een eerste topologieschets.

Je tekening moet minstens tonen:

- toestelnamen;
- verbindingen;
- VLAN's of subnetten;
- internetedge;
- interne serverzone;
- eventuele DMZ;
- managementzone.

Controlepunt:

> Kan iemand anders aan de hand van je tekening zien waar de securitygrenzen zouden moeten liggen?

---

## 8. Stap 2: breng VLAN's en subnetten in kaart

Onderzoek welke VLAN's en subnetten gebruikt worden.

Gebruik bijvoorbeeld:

```text
show vlan brief
show interfaces trunk
show ip interface brief
show running-config
```

Vul deze tabel in:

| VLAN | Naam | Subnet | Gateway | Doel |
|---:|---|---|---|---|
| ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... |

Beantwoord:

- Is elk VLAN duidelijk benoemd?
- Hoort elk subnet logisch bij een functie?
- Zijn er VLAN's die te veel verschillende functies combineren?
- Is er een apart managementnetwerk?
- Is er een apart gastennetwerk?
- Is er een apart DMZ-netwerk?

Controlepunt:

> Kan je voor elk VLAN uitleggen waarom het bestaat?

---

## 9. Stap 3: bepaal de securityzones

Vertaal VLAN's en subnetten naar securityzones.

Mogelijke zones:

- Internet;
- DMZ;
- Staff;
- Finance;
- IT;
- Servers;
- Guests;
- IoT;
- Management.

Vul deze tabel in:

| Zone | VLAN's of subnetten | Vertrouwensniveau | Waarom? |
|---|---|---|---|
| ... | ... | ... | ... |
| ... | ... | ... | ... |

Beantwoord:

- Welke zone vertrouw je het minst?
- Welke zone bevat de meest gevoelige systemen?
- Welke zone mag netwerktoestellen beheren?
- Welke zone mag alleen internettoegang hebben?
- Welke zones mogen nooit rechtstreeks met elkaar communiceren?

Controlepunt:

> Maak duidelijk onderscheid tussen VLAN, subnet en zone.

---

## 10. Stap 4: duid trust boundaries aan

Duid op je schema de belangrijkste trust boundaries aan.

Denk aan grenzen tussen:

- Internet en DMZ;
- Internet en intern netwerk;
- DMZ en intern netwerk;
- Guests en intern netwerk;
- IoT en servers;
- Staff en management;
- IT en management;
- VPN of externe toegang en interne systemen, indien aanwezig.

Vul deze tabel in:

| Trust boundary | Waarom is dit een grens? | Controle nodig? |
|---|---|---|
| Internet - DMZ | ... | ... |
| DMZ - Intern | ... | ... |
| Guests - Intern | ... | ... |
| Staff - Management | ... | ... |
| ... | ... | ... |

Controlepunt:

> Een trust boundary zonder filterregel of controlepunt is vooral een tekening, geen beveiliging.

---

## 11. Stap 5: ontwerp of beoordeel de DMZ

Onderzoek waar de publieke webdienst staat.

Beantwoord:

- Staat de publieke webserver in een apart DMZ-subnet?
- Staat de webserver per ongeluk in het interne servernetwerk?
- Welke poorten moeten vanaf internet bereikbaar zijn?
- Mag internet rechtstreeks naar interne servers?
- Mag een DMZ-server verbinding starten naar interne servers?
- Wie mag de DMZ-server beheren?
- Vanuit welke zone mag beheer gebeuren?

Vul deze tabel in:

| Dienst | Huidige zone | Gewenste zone | Toegang vanaf internet | Opmerking |
|---|---|---|---|---|
| Publieke website | ... | DMZ | HTTPS | ... |
| Interne applicatie | ... | Servers | nee | ... |
| Beheerinterface | ... | Management | nee vanaf internet | ... |

Controlepunt:

> Een server die vanaf internet bereikbaar is, hoort niet automatisch in het interne servernetwerk.

---

## 12. Stap 6: analyseer huidige toegangsregels

Onderzoek bestaande ACL's of firewallregels.

Gebruik bijvoorbeeld:

```text
show access-lists
show running-config
show ip interface brief
```

Beantwoord:

- Welke ACL's bestaan er?
- Op welke interface en in welke richting zijn ze toegepast?
- Welke regels zijn te breed?
- Staat er ergens `permit ip any any`?
- Wordt guest-verkeer naar interne subnetten geblokkeerd?
- Is management alleen bereikbaar vanaf IT?
- Wordt de DMZ afgeschermd van interne servers?
- Wordt internetverkeer naar interne servers geblokkeerd?

Vul deze tabel in:

| ACL of regel | Plaats | Bedoeling | Probleem of risico |
|---|---|---|---|
| ... | ... | ... | ... |
| ... | ... | ... | ... |

Controlepunt:

> Een regel kan inhoudelijk goed lijken, maar fout geplaatst zijn. Controleer dus ook het verkeerspad.

---

## 13. Stap 7: maak een firewallregelmatrix

Maak een gewenste firewallregelmatrix volgens least privilege.

Gebruik deze tabel als startpunt:

| Bronzone | Doelzone | Dienst | Actie | Reden |
|---|---|---|---|---|
| Staff | Servers | HTTPS naar intranet/app | allow | nodige bedrijfsapp |
| Staff | Management | any | deny | geen beheerrechten |
| Finance | Finance-server | nodige appdienst | allow | financeproces |
| Guests | Internet | DNS/HTTP/HTTPS | allow | gastinternet |
| Guests | Internal | any | deny | isolatie |
| IoT | Servers | alleen noodzakelijke dienst | allow beperkt | devicefunctie |
| IoT | Management | any | deny | beheer beschermen |
| IT | Management | SSH/HTTPS | allow | beheer |
| Internet | DMZ-webserver | HTTPS | allow | publieke website |
| Internet | Internal | any | deny | intern beschermen |
| DMZ | Internal | specifiek of deny | deny tenzij nodig | laterale beweging beperken |
| DMZ | Management | any | deny | beheer beschermen |

Voeg zelf regels toe waar nodig.

Controlepunt:

> Kan je bij elke allow-regel uitleggen welke businessbehoefte ze ondersteunt?

---

## 14. Stap 8: maak een testplan

Maak een testplan dat zowel toegelaten als verboden verkeer test.

Vul deze tabel in:

| Test | Bron | Doel | Dienst | Verwacht | Werkelijk | Conclusie |
|---|---|---|---|---|---|---|
| Staff naar intranet | ... | ... | HTTPS | werkt | ... | ... |
| Guest naar internet | ... | ... | HTTP/HTTPS | werkt | ... | ... |
| Guest naar server | ... | ... | ICMP/HTTP | faalt | ... | ... |
| Staff naar management | ... | ... | SSH/HTTPS | faalt | ... | ... |
| IT naar management | ... | ... | SSH | werkt | ... | ... |
| Internet naar DMZ-web | ... | ... | HTTPS | werkt | ... | ... |
| Internet naar interne server | ... | ... | HTTP/HTTPS | faalt | ... | ... |
| DMZ naar management | ... | ... | SSH/HTTPS | faalt | ... | ... |

Controlepunt:

> Als je alleen testen opneemt die moeten werken, test je security maar half.

---

## 15. Stap 9: formuleer risico's

Maak een risicoanalyse.

Een goed risico is concreet.

Niet:

> Firewall is niet goed.

Wel:

> Het guest VLAN kan de interne applicatieserver bereiken. Daardoor kan een onbeheerd gasttoestel interne systemen scannen of aanvallen.

Vul deze tabel in:

| Vaststelling | Risico | Impact | Mogelijke verbetering |
|---|---|---|---|
| ... | ... | ... | ... |
| ... | ... | ... | ... |

Zoek minstens zes risico's.

Denk aan:

- guest access;
- managementtoegang;
- DMZ-plaatsing;
- te brede servertoegang;
- IoT-toegang;
- finance-data;
- internet naar interne systemen;
- regels zonder documentatie;
- default allow;
- ontbrekende logging.

Controlepunt:

> Kan je bij elk risico zeggen welke zone te veel toegang krijgt?

---

## 16. Stap 10: formuleer verbeterpunten

Formuleer concrete verbeterpunten.

Een goed verbeterpunt is toetsbaar.

Niet:

> Maak security beter.

Wel:

> Blokkeer verkeer van Guests naar alle interne `10.30.0.0/16`-subnetten, maar laat DNS, HTTP en HTTPS naar internet toe.

Vul deze tabel in:

| Verbeterpunt | Welk risico lost dit op? | Hoe test je dit? |
|---|---|---|
| ... | ... | ... |
| ... | ... | ... |

Zoek minstens zes verbeterpunten.

Controlepunt:

> Elk verbeterpunt moet gekoppeld zijn aan een risico en een test.

---

## 17. Eindconclusie

Schrijf een conclusie van 10 tot 15 regels.

Je conclusie moet minstens antwoorden op:

- Is het netwerk securitymatig enterprise-ready?
- Welke zones zijn goed herkenbaar?
- Welke trust boundaries ontbreken of worden onvoldoende afgedwongen?
- Is de DMZ correct ontworpen?
- Welke toegang is te breed?
- Welke verbeteringen hebben prioriteit?

Gebruik deze structuur:

```text
Het netwerk bevat ...

Sterke punten zijn ...

Belangrijkste securityrisico's zijn ...

De eerste verbeteringen zijn ...

Mijn eindconclusie is ...
```

Controlepunt:

> Je conclusie moet securitybeleid koppelen aan bedrijfsimpact. Schrijf dus niet alleen "ACL fout".

---

## 18. In te dienen

Lever een kort securityarchitectuurverslag in.

Je verslag bevat minstens:

1. topologieschets;
2. VLAN- en subnettabel;
3. zoneschema;
4. trust boundary-overzicht;
5. DMZ-beoordeling of DMZ-ontwerp;
6. analyse van bestaande ACL's of firewallregels;
7. firewallregelmatrix;
8. testplan met verwachte en werkelijke resultaten;
9. risicoanalyse;
10. verbeterpunten;
11. eindconclusie.

Het verslag hoeft niet lang te zijn. Het moet wel duidelijk, controleerbaar en professioneel zijn.

---

## 19. Typische valkuilen

| Valkuil | Waarom is dit een probleem? |
|---|---|
| Alleen kijken of ping werkt | Bereikbaarheid kan net een securityprobleem zijn |
| VLAN's gelijkstellen aan security | Zonder regels wordt segmentatie niet afgedwongen |
| DMZ vergeten | Publieke systemen komen te dicht bij interne servers |
| Managementnetwerk te breed bereikbaar laten | Beheerinterfaces worden doelwit |
| Guests alleen internet laten testen | Je moet ook testen dat intern geblokkeerd is |
| `permit ip any any` accepteren | Te brede toegang wordt normaal gemaakt |
| Geen reden noteren bij allow-regels | Regels worden later onbeheerbaar |
| Alleen north-south verkeer bekijken | Interne laterale beweging blijft mogelijk |
| ACL-syntax centraal zetten | Het ontwerp en beleid zijn belangrijker |
| Verbeterpunten vaag formuleren | Je kan ze niet uitvoeren of testen |

---

## 20. Hulpvragen

Gebruik deze vragen als je vastloopt:

- Welke zone is de bron?
- Welke zone is het doel?
- Vertrouwen we de bronzone?
- Is deze verkeersstroom nodig voor het bedrijf?
- Welke dienst of poort is echt nodig?
- Staat het doel in de juiste zone?
- Waar passeert dit verkeer?
- Waar kan je dit verkeer het best blokkeren?
- Wat is het verwachte gedrag?
- Heb je ook getest dat verboden verkeer geblokkeerd wordt?
- Is dit north-south of east-west traffic?
- Welke regel zou je kunnen verwijderen zonder functionaliteit te breken?

---

## 21. Eindvraag

Sluit je verslag af met een antwoord op deze vraag:

> Waarom is een firewallregelmatrix belangrijker dan meteen beginnen met ACL's schrijven?

