# Enterprise Networking

Welkom in de repository voor het opleidingsonderdeel **Enterprise Networking**. Je vindt hier de cursus, workshops, labbestanden en de integratieopdracht. Werk de hoofdstukken in de aangegeven volgorde af: de latere labs bouwen voort op de kennis en aanpak uit de eerdere hoofdstukken.

## Snel starten

1. Clone of download deze repository en open ze in een Markdown-editor of op GitHub.
2. Lees eerst het cursusmateriaal van het hoofdstuk dat je volgt.
3. Open daarna uitsluitend het bestand in de map `student/` van de bijbehorende workshop of opdracht.
4. Werk stap voor stap, voer de gevraagde tests uit en bewaar je bewijs volgens de instructies in de opdracht.
5. Dien alleen je eigen werk en de gevraagde bestanden in via de afgesproken leeromgeving of Git-repository.

Gebruik modeloplossingen alleen wanneer je docent dat uitdrukkelijk toestaat. Ze zijn bedoeld om je werk te controleren en niet als vertrekpunt voor je eigen oplossing.

## Leerpad

| Hoofdstuk | Onderwerp | Jouw materiaal |
|---|---|---|
| 1 | Enterprise baseline en design | [Cursus](Ch1/cursus/ch1-enterprise-baseline-cursus.md) · [Workshop](Ch1/workshop/student/ch1-enterprise-baseline-workshop-student.md) · [Thuisoefening](Ch1/thuisopdracht/student/ch1-enterprise-baseline-thuisopdracht-student.md) |
| 2 | Switching- en routingessentials | [Cursus](Ch2/cursus/ch2-switching-routing-essentials-cursus.md) · [Workshop](Ch2/workshop/student/ch2-switching-routing-essentials-workshop-student.md) |
| 3 | Security architecture | [Cursus](Ch3/cursus/ch3-security-architecture-cursus.md) · [Workshop](Ch3/workshop/student/ch3-security-architecture-workshop-student.md) · [Packet Tracer-opdracht](Ch3/Opdracht/packet-tracer/ch3-security-architecture-student.pkt) |
| 4 | High availability en secure management | [Cursus](Ch4/cursus/ch4-high-availability-secure-management-cursus.md) · [Workshop](Ch4/workshop/student/ch4-high-availability-secure-management-workshop-student.md) |
| 5 | VPN-concepten | [Cursus](Ch5/cursus/ch5-vpn-concepten-cursus.md) · [Workshop](Ch5/workshop/student/ch5-vpn-concepten-workshop-student.md) |
| 6 | VPN-policy en routed access | [Cursus](Ch6/cursus/ch6-vpn-policy-routed-access-cursus.md) · [Workshop](Ch6/workshop/student/ch6-vpn-policy-routed-access-workshop-student.md) |
| 7 | VPN-security, NAT traversal en zichtbaarheid | [Cursus](Ch7/cursus/ch7-vpn-security-nat-traversal-cursus.md) · [Workshop](Ch7/workshop/student/ch7-vpn-security-nat-traversal-workshop-student.md) |
| 8 | Reverse proxies | [Cursus](Ch8/cursus/ch8-reverse-proxies-cursus.md) · [Workshop](Ch8/workshop/student/ch8-reverse-proxies-workshop-student.md) |
| 9 | Authentik en identity providers | [Cursus](Ch9/cursus/ch9-authentik-identity-providers-cursus.md) · [Workshop](Ch9/workshop/student/ch9-authentik-identity-providers-workshop-student.md) |
| 10 | Identity-aware access met Traefik en Authentik | [Cursus](Ch10/cursus/ch10-identity-aware-access-cursus.md) · [Workshop](Ch10/workshop/student/ch10-identity-aware-access-workshop-student.md) |
| 11 | Integratieopdracht: PixelPeak Studios | [Opdracht](Ch11/opdracht/student/ch11-enterprise-integratieopdracht-student.md) |

## Waar vind je de bestanden?

Elke hoofdstukmap bevat materiaal per type activiteit:

- `cursus/`: theorie en achtergrond voor het hoofdstuk.
- `workshop/student/`: het werkdocument dat je tijdens de workshop volgt.
- `workshop/configs/student/`: starterconfiguraties, testbladen of aanvullende bestanden wanneer de workshop die nodig heeft.
- `packet-tracer/` of `Opdracht/packet-tracer/`: Cisco Packet Tracer-bestanden. Kies altijd het bestand met `student`, `start` of `base` in de naam.
- `thuisopdracht/student/`: zelfstandig uit te voeren oefening.
- `Ch11/opdracht/student/`: de eindopdracht en de startbestanden daarvoor.

De mappen `oplossing/`, `teacher/` en bestanden met `solution` of `modeloplossing` zijn geen startpunt voor je werk.

## Benodigdheden

De exacte vereisten staan steeds in het studentdocument van een workshop. Over het volledige traject heb je doorgaans het volgende nodig:

- Cisco Packet Tracer voor hoofdstuk 1 tot en met 4;
- een terminal en een Markdown-editor of tekstverwerker;
- voor de VPN-labs: een toegewezen Debian-VM, internettoegang en alleen de rechten die de docent voorziet;
- voor hoofdstuk 8 tot en met 10: Docker Desktop of Docker Engine, Docker Compose v2, een browser en `curl`/`curl.exe`;
- voor de MFA-labs: een TOTP-compatibele authenticator;
- voor de integratieopdracht: de Proxmox-omgeving en overige toegang die je docent aan je team toewijst.

Controleer altijd eerst de sectie **Benodigdheden** in het huidige workshopdocument. Installeer of wijzig niets op het schoolnetwerk buiten de expliciete labo-instructies.

## Veilig, zorgvuldig en reproduceerbaar werken

Je werkt uitsluitend in de toegewezen labo-omgeving en binnen de grenzen van de opdracht. Lees vóór de VPN-hoofdstukken de [verklaring verantwoord gebruik van VPN-technologie](Ch5/verklaring-verantwoord-gebruik.md). Vraag je docent om toestemming wanneer de impact van een netwerk-, routing-, firewall- of VPN-wijziging niet duidelijk is.

Zet nooit secrets of persoonsgegevens in Git, screenshots of in te dienen documenten. Hieronder vallen onder meer wachtwoorden, auth keys, tokens, cookies, private keys, OIDC-secrets, TOTP-QR-codes en recoverycodes. Gebruik waar nodig een lokaal `.env`-bestand en een `.env.example` met uitsluitend lege of fictieve waarden.

Werk stapsgewijs: wijzig één onderdeel tegelijk, test het verwachte én het ongewenste gedrag, en noteer kort wat je hebt aangepast en wat de test aantoonde. Dat maakt je oplossing beter te troubleshooten en te verdedigen.

## De integratieopdracht

In hoofdstuk 11 combineer je netwerksegmentatie, VPN-policy, reverse proxy, centrale identiteit en applicatiebeveiliging in een teamproject. Begin met de [volledige opdrachtbeschrijving](Ch11/opdracht/student/ch11-enterprise-integratieopdracht-student.md). Gebruik Git vanaf de eerste week, maak kleine betekenisvolle commits en documenteer ontwerpkeuzes, tests en incidenten. De opdracht bevat ook de vereiste structuur voor de in te dienen repository.

## Hulp nodig?

Controleer eerst de foutscenario's, hints en testlijsten in je workshopdocument. Leg vervolgens aan je docent voor wat je probeerde, welke configuratie relevant is en wat je precies verwachtte en observeerde. Deel daarbij nooit gevoelige gegevens.
