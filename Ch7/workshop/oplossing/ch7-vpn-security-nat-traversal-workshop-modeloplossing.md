# Workshop 7 - VPN security en NAT traversal onderzoeken met Tailscale

## Modeloplossing voor studenten

## 1. Korte samenvatting

De Debian-VM bleef als server in Devbit staan. De laptop werd eerst met Devbit en daarna met eduroam/campusroam verbonden.

Op beide endpoints draaide Tailscale. De tijdelijke HTTP- en `iperf3`-dienst luisterde alleen op het Tailscale-IP van de VM.

De student vergeleek per netwerk:

- underlayadres en default route;
- Tailscale-overlayadres;
- `tailscale netcheck`;
- `tailscale ping` en `tailscale status`;
- HTTP-bereikbaarheid;
- latency en throughput;
- zichtbare binnen- en buitenpakketten.

De exacte adressen, latency, throughput en connection types verschillen per student en tijdstip.

Kernconclusie:

> Tailscale houdt de logische identiteit en het overlayadres van een device stabiel, terwijl NAT traversal voor elk fysiek netwerk opnieuw een bruikbaar datapad zoekt. Dat pad kan direct of relayed zijn zonder dat de end-to-end WireGuard-encryptie verdwijnt.

---

## 2. Underlay en overlay

Voorbeeldinventaris:

| Eigenschap | Voorbeeld |
|---|---|
| VM-hostname | `ch7-vpn-server` |
| VM Devbit-IP | `10.x.x.x` |
| VM Tailscale-IP | `100.x.x.x` |
| laptop Devbit-IP | `10.x.x.x` |
| laptop campusroam-IP | ander privaat of publiek adres |
| laptop Tailscale-IP | hetzelfde `100.x.x.x`-adres op beide netwerken |

Uitleg:

- Devbit en campusroam zijn underlaynetwerken;
- `100.x.x.x` is het Tailscale-overlayadres;
- bij een netwerkwissel verandert de lokale interface en default route;
- de tailnet-identiteit en het Tailscale-IP blijven normaal behouden;
- Tailscale ontdekt daarna nieuwe endpoints en onderhandelt opnieuw een pad.

Een Devbit-IP is niet automatisch routeerbaar vanuit campusroam. Het Tailscale-IP is alleen bruikbaar via de actieve Tailscale-client en toegestane tailnetpolicy.

---

## 3. Installatie en device-authenticatie

Op de Debian-VM:

```text
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Verwachte controles:

```text
systemctl is-active tailscaled
tailscale status
tailscale ip -4
ip -br address show tailscale0
```

Verwacht:

- `tailscaled` is `active`;
- VM en laptop zijn peers in dezelfde tailnet;
- de VM heeft een Tailscale-IPv4;
- `tailscale0` bestaat.

Securityuitleg:

| Begrip | In dit labo |
|---|---|
| authenticatie | laptop en VM bewijzen hun device-identiteit met cryptografische keys |
| encryptie | inhoud wordt in de WireGuard-data plane versleuteld |
| integriteit | gewijzigde pakketten worden niet als geldig aanvaard |
| autorisatie | tailnetpolicy bepaalt welke bron naar welke service mag |

Een auth key of login-URL is gevoelig onboardingmateriaal. De private device key blijft op het endpoint en wordt niet gedeeld.

---

## 4. Serverdienst alleen op Tailscale

De tijdelijke dienst werd gestart op het Tailscale-IP:

```text
CH7_TS_IP="$(tailscale ip -4)"
nohup python3 -m http.server 8080 --bind "$CH7_TS_IP" --directory "$HOME/ch7-vpn-lab" > "$HOME/ch7-http.log" 2>&1 &
```

Verwachte listener:

```text
LISTEN ... 100.x.x.x:8080 ...
```

Niet verwacht:

```text
0.0.0.0:8080
```

Interpretatie:

- de applicatie luistert op de overlayinterface;
- een request naar het Devbit-IP bereikt deze listener niet;
- ook een werkende VPN maakt ongebruikte poorten niet vanzelf open;
- servicebinding is defense in depth naast ACL en host firewall.

---

## 5. Control plane en data plane

| Observatie | Classificatie | Uitleg |
|---|---|---|
| VM aanmelden | control plane | identity en device worden geregistreerd |
| public keys verspreiden | control plane | peers leren elkaars cryptografische identiteit |
| endpoints uitwisselen | control plane/connectieopbouw | peers leren mogelijke paden kennen |
| ACL-policy ontvangen | control plane | toegangsregels worden verdeeld |
| `curl` naar TCP/8080 | data plane | gebruikerspayload tussen laptop en VM |
| `iperf3`-transfer | data plane | meetverkeer door de tunnel |
| WireGuard-pakketten via DERP | data plane via relay | payload blijft end-to-end versleuteld |
| device verwijderen | control plane | identity/lifecycle wordt aangepast |

Bij een directe verbinding transporteert geen centrale Tailscale-relay de HTTP-payload. De versleutelde pakketten gaan rechtstreeks tussen de endpoints.

---

## 6. `tailscale netcheck`

Correcte interpretatie:

| Veld | Betekenis |
|---|---|
| `UDP: true` | STUN-probes bereikten de testservers via outbound UDP; direct verkeer heeft meer kans |
| `UDP: false` | outbound UDP werd niet succesvol vastgesteld; relaygebruik is waarschijnlijker |
| `IPv4` | publiek IPv4-endpoint zoals door de buitenwereld gezien |
| `IPv6` | bruikbare IPv6-connectiviteit indien aanwezig |
| `MappingVariesByDestIP: false` | mapping is relatief voorspelbaar over bestemmingen |
| `MappingVariesByDestIP: true` | moeilijker NAT-gedrag; mapping hangt af van bestemming |
| `PortMapping` | gedetecteerde UPnP-, NAT-PMP- of PCP-mogelijkheid |
| `Nearest DERP` | relayregio met de laagste gemeten latency vanaf dit endpoint |

Antwoorden:

1. Een publiek endpoint is niet noodzakelijk gelijk aan het lokale laptop-IP. NAT/PAT kan adres en poort vertalen.
2. STUN-achtige endpoint discovery laat een externe server rapporteren van welk endpoint de probe kwam.
3. Endpoint discovery vervoert niet de HTTP-applicatiedata. Ze helpt peers een pad te vinden.
4. Als de mapping per bestemming varieert, is het lastiger een endpoint te voorspellen dat ook voor de andere peer werkt.
5. Een leeg `PortMapping`-veld betekent dat geen bruikbaar port-mappingprotocol werd gemeld. Het sluit NAT of een gewone tijdelijke NAT mapping niet uit.
6. Een NAT mapping ontstaat normaal door uitgaand verkeer en vervalt na een timeout. Een port mapping via UPnP, NAT-PMP of PCP vraagt explicieter om een voorspelbare vertaling.

`netcheck` op de laptop alleen beschrijft niet de volledige verbinding. Het NAT- en firewallgedrag aan VM-zijde telt eveneens mee.

---

## 7. NAT traversal en hole punching

Sterk vereenvoudigd gebeurde dit:

```text
1. Laptop en VM melden endpointinformatie aan de coördinatielaag.
2. Beide peers kennen mogelijke lokale, publieke en relaypaden.
3. Beide peers sturen uitgaand UDP-verkeer.
4. NAT en stateful firewalls maken tijdelijke mappings/state.
5. Als de mappings compatibel zijn, ontstaat een direct UDP-pad.
6. Zo niet, dan blijft een peer relay of DERP beschikbaar.
```

Dit vereist geen nieuwe willekeurige inbound sessie die een student op de campusrouter opent. Beide endpoints starten zelf uitgaand verkeer. Dat is waarom stateful firewalls passend antwoordverkeer kunnen toelaten.

NAT en firewall zijn niet hetzelfde:

| Component | Hoofdvraag |
|---|---|
| NAT/PAT | hoe worden adressen en poorten vertaald? |
| stateful firewall | welk verkeer mag starten en welk antwoordverkeer hoort bij bestaande state? |

---

## 8. Connection type interpreteren

### Geldig voorbeeld A: eerst DERP, daarna direct

Illustratieve output:

```text
pong from ch7-vpn-server (100.x.x.x) via DERP(ams) in 28ms
pong from ch7-vpn-server (100.x.x.x) via 193.***.***.42:41641 in 12ms
```

Interpretatie:

- DERP hielp bij de eerste connectieopbouw;
- daarna slaagde NAT traversal;
- het stabiele datapad is direct UDP;
- `tailscale status` hoort na actief verkeer `direct` te tonen.

### Geldig voorbeeld B: blijvend DERP

Illustratieve output:

```text
pong from ch7-vpn-server (100.x.x.x) via DERP(ams) in 31ms
...
direct connection not established
```

Interpretatie:

- de peers bleven bereikbaar;
- direct UDP lukte binnen de test niet;
- de data plane liep via DERP;
- de WireGuard-inhoud bleef end-to-end versleuteld;
- latency en throughput kunnen slechter zijn.

### Geldig voorbeeld C: peer relay

`peer-relay` betekent dat een hiervoor geconfigureerd device in dezelfde tailnet als tussenpunt dient. Ook hier blijft de payload end-to-end versleuteld.

---

## 9. Vergelijking Devbit en campusroam

Voorbeeld van een correcte tabel:

| Meetpunt | Devbit | campusroam |
|---|---|---|
| lokaal laptop-IP | Devbit-adres | ander adres |
| default gateway | Devbit-gateway | campusroam-gateway |
| laptop Tailscale-IP | `100.x.x.x` | hetzelfde `100.x.x.x` |
| publiek endpoint | endpoint A | endpoint B |
| UDP | true | true of false |
| mapping varieert | gemeten waarde | gemeten waarde |
| eerste pad | vaak DERP | vaak DERP |
| stabiele pad | werkelijk gemeten | werkelijk gemeten |
| HTTP via Tailscale | werkt | werkt |
| HTTP via Devbit-IP | lokaal mogelijk geblokkeerd | faalt verwacht |

Sterke conclusie:

> Het Tailscale-IP bleef stabiel omdat het bij de tailnetidentiteit hoort. Door de netwerkwissel veranderden underlayadres, route en publiek endpoint. Tailscale moest daarom endpoint discovery en path selection opnieuw uitvoeren. Dat kan hetzelfde of een ander connection type opleveren.

Een veranderd publiek endpoint betekent niet dat NAT traversal mislukte. Het is een verwachte consequentie van een andere underlay.

---

## 10. Performanceanalyse

De student gebruikt alleen eigen meetwaarden. Een correct antwoord bevat minstens:

- connection type tijdens de transfer;
- richting;
- latency;
- throughput;
- duur van de test;
- netwerkcontext;
- voorbehoud bij één meting.

Algemene verwachting:

| Pad | Typische eigenschap |
|---|---|
| direct | minder hops, vaak lagere latency en hogere throughput |
| peer relay | extra tailnet-hop, vaak gunstiger dan een verre DERP |
| DERP | robuuste fallback, extra pad en beperkte QoS |

Andere mogelijke bottlenecks:

- wifi-signaal en interferentie;
- congestie;
- uplink/downlink-asymmetrie;
- CPU-encryptiekost;
- packet loss en retransmits;
- jitter;
- MTU;
- de applicatie zelf.

Daarom is `direct` niet hetzelfde als `gegarandeerd snel`.

---

## 11. Encryptiegrens en packet capture

### Op `tailscale0`

Verwacht:

- inner TCP/8080;
- HTTP-method en pad;
- `X-Ch7-Marker`;
- inhoud van de testpagina.

Reden:

> De capture gebeurt op het endpoint nadat Tailscale het pakket heeft ontsleuteld en aan de virtuele interface aanbiedt.

### Op de fysieke Devbit-interface

Verwacht:

- buitenste bron- en bestemmings-IP's;
- UDP en poorten bij direct verkeer;
- mogelijk TCP/443 naar DERP bij relay;
- timing, volume en packet sizes.

Gerichte filters:

| Pad | Filterbasis |
|---|---|
| direct | peer-IP en peerpoort uit `tailscale status` plus lokale UDP-poort uit `ss -lunp` |
| DERP | DERP-IP en remote TCP/443 plus lokale tijdelijke poort uit `ss -ntpi` |
| peer relay | concreet peer-relayendpoint uit `tailscale status` |

Een direct voorbeeldfilter:

```text
udp and host <PEER-ENDPOINT-IP> and port <PEER-ENDPOINT-POORT> and port <LOKALE-TAILSCALE-UDP-POORT>
```

Een DERP-voorbeeldfilter:

```text
tcp and host <DERP-IP> and port 443 and port <LOKALE-DERP-TCP-POORT>
```

`tcp port 443` zonder host en lokale socketpoort is te breed. De korte capture wordt daarom naar een `.pcap` geschreven en achteraf gelezen. Bij meerdere `tailscaled`-sockets helpen de bytecounters van `ss -ntpi` om de actieve DERP-socket te herkennen.

Niet verwacht als leesbare VPN-payload:

- de HTTP-marker;
- het HTTP-pad;
- de testpagina;
- applicatieheaders.

De afwezigheid van een marker in een korte capture is op zichzelf geen cryptografisch bewijs. De combinatie van interfaceplaatsing, WireGuard-ontwerp en consistente captureobservaties ondersteunt de uitleg.

---

## 12. Split tunnel

Zonder geconfigureerde exit node:

```text
100.x.x.x/overlaybestemming -> Tailscale
gewone internetbestemming -> lokale default gateway
```

Gevolg:

- de VM-service loopt door de Tailscale-data plane;
- gewone websites lopen via Devbit of campusroam;
- de lokale netwerkbeheerder blijft internetbestemmingen buiten de VPN zien;
- de tailnetbeheerder krijgt niet automatisch alle internetflows te zien.

Bij full tunnel via een exit node zou de lokale netwerkbeheerder vooral het VPN-pad zien, terwijl de exit-nodebeheerder meer externe bestemmingsmetadata krijgt. Vertrouwen en zichtbaarheid verschuiven dus.

---

## 13. Negatieve securitytests

| Eigenschap | Correcte toepassing in het labo |
|---|---|
| vertrouwelijkheid | tussenliggende netwerken kunnen de HTTP-payload in de WireGuard-tunnel niet normaal lezen |
| integriteit | gewijzigde versleutelde pakketten slagen niet voor de cryptografische controle |
| authenticatie | peers bewijzen bezit van hun private device key |
| autorisatie | tailnetpolicy bepaalt welke geauthenticeerde bron een service mag bereiken |
| replaybescherming | oude datapakketten kunnen niet zomaar opnieuw als geldig worden aangeboden |
| forward secrecy | tijdelijke sessiesleutels beperken de impact van later sleutelverlies op ouder verkeer |
| beschikbaarheid | niet gegarandeerd; een netwerk kan verkeer nog blokkeren, vertragen of rate-limiten |

| Test | Verwacht | Betekenis |
|---|---|---|
| Tailscale-IP:8080 met actieve client | werkt | toegestaan overlaypad en actieve service |
| Devbit-IP:8080 vanaf campusroam | faalt | geen rechtstreeks pad en verkeerde servicebinding |
| Tailscale-IP:8081 | faalt | geen listener; VPN opent niet alle poorten |
| Tailscale-IP:8080 met Tailscale uit | faalt | geen actieve tailnetroute |

Deze tests bewijzen niet dat de HTTP-applicatie gebruikersauthenticatie heeft. De demo-applicatie heeft juist geen login.

Aanvullende beveiliging blijft nodig:

- least-privilege tailnetpolicy;
- host firewall;
- patching;
- applicatieauthenticatie en autorisatie;
- logging;
- device lifecycle.

---

## 14. DNS en MagicDNS

Als MagicDNS actief is, hoort de device- of MagicDNS-naam naar het Tailscale-IP te verwijzen. Daardoor kunnen studenten dezelfde HTTP-service via naam en via `100.x.x.x` testen.

Correcte analyse:

- IP-connectiviteit kan werken terwijl naamresolutie faalt;
- MagicDNS behandelt namen van tailnetdevices;
- Split DNS stuurt alleen geselecteerde zones naar een specifieke resolver;
- gewone DNS buiten de VPN kan interne hostnamen en gebruikspatronen lekken;
- welke querymetadata wordt bewaard, hangt van resolver en loggingbeleid af.

Als MagicDNS niet actief is, is `naam werkt niet, IP werkt wel` een geldige configuratie-uitkomst en geen bewijs dat de WireGuard-data plane defect is.

---

## 15. Zichtbaarheid

| Partij | Kan waarschijnlijk zien | Kan normaal niet zien |
|---|---|---|
| campusroambeheerder | laptopidentificatie op WLAN, lokaal IP, buitenste bestemmingen, poorten, timing, volume, mogelijk VPN/relaygebruik | HTTP-pad, marker en pagina binnen de tunnel |
| Devbit-firewallbeheerder | VM-IP, buitenste peer- of relayflows, UDP/TCP, timing en volume | inner HTTP-inhoud |
| ISP/upstream | publieke endpoints, protocol, volume en timing | private inner IP's en applicatiepayload |
| tailnetbeheerder | users, devices, public keys, names, tags, routes, policy, online status en afhankelijk van logging flowmetadata | niet automatisch plaintext van end-to-end datastromen |
| DERP-beheerder | bronverbindingen naar relay, relayregio, timing en volume | WireGuard-plaintext, HTTP-pad en bestanden |
| Debian-server | ontsleutelde request, bron binnen tailnet, serviceport en applicatielog | niet noodzakelijk volledige campusroute vóór aankomst |

DNS-nuance:

- lokale DNS kan namen lekken;
- MagicDNS-naamresolutie wordt door Tailscale behandeld;
- logginginstellingen bepalen welke partij querymetadata bewaart;
- encryptie van data verbergt niet automatisch alle naammetadata.

---

## 16. Firewall- en port-forwardingadvies

Voorbeeldbeoordeling:

| Maatregel | Beoordeling voor tijdelijk studentenlabo |
|---|---|
| outbound UDP toelaten | kan direct verkeer helpen; alleen door netwerkbeheerder na policyreview |
| beperkte UDP-regel voor vaste serverrol | verdedigbaar voor beheerde, langdurige infrastructuur; hier meestal niet nodig |
| inbound UDP naar alle clients | afwijzen; te breed aanvalsoppervlak |
| port forwarding naar tijdelijke VM | meestal afwijzen; lifecycle en noodzaak onvoldoende |
| DERP blokkeren | afwijzen; verwijdert veilige fallback en kan connectiviteit breken |
| relay accepteren | passend als performance voldoende is en wijzigingsrisico groter is |

Sterk advies:

> Wijzig niets alleen omdat relay zichtbaar is. Bevestig eerst een reëel performanceprobleem. Als vaste infrastructuur structureel relayed blijft, kan de beheerder minimale outbound UDP of een specifieke, gedocumenteerde UDP-bereikbaarheid onderzoeken. Voor een tijdelijke studenten-VM zonder routerbeheer is DERP accepteren meestal de juiste keuze.

Port forwarding omzeilt de tailnetpolicy niet en maakt interne applicatiepoorten niet vanzelf veilig. Het is hoogstens een pad- en performancekeuze voor de VPN-endpoint.

---

## 17. MTU en beschikbaarheid

Een werkende ping met 1200 bytes toont slechts dat deze pakketgrootte in die test werkte. Hij bewijst niet de volledige path MTU.

Mogelijke MTU-symptomen:

- kleine pings werken maar grotere transfers hangen;
- websites laden gedeeltelijk;
- TLS-sessies falen vreemd;
- throughput is onverwacht laag;
- bepaalde applicaties werken niet consistent.

Een netwerk kan bovendien VPN-verkeer droppen, vertragen of rate-limiten zonder de inhoud te ontsleutelen. Encryptie beschermt confidentiality en integrity, niet availability.

---

## 18. Typische misverstanden

| Misverstand | Correctie |
|---|---|
| VPN maakt mij anoniem | VPN verschuift vertrouwen en metadatazicht |
| encryptie maakt alles veilig | endpoint, policy en applicatie blijven bepalend |
| relay is onveilig | payload blijft end-to-end versleuteld; performance en metadata veranderen |
| direct is altijd beter | meestal sneller, maar enterprisebeleid kan gecontroleerde paden vereisen |
| firewall blokkeert, dus `allow any any` | eerst laag, pad en noodzakelijke minimale regel bepalen |
| werkende ping bewijst werkende applicatie | servicebinding, poort, policy en applicatie moeten apart getest worden |

---

## 19. Eindantwoord

De Debian-server blijft via hetzelfde Tailscale-adres bereikbaar omdat het overlayadres gekoppeld is aan de tailnetidentiteit van de server en niet aan het tijdelijke fysieke netwerk van de laptop.

Wanneer de laptop van Devbit naar eduroam of campusroam wisselt, veranderen het lokale adres, de default route en meestal het publiek waargenomen endpoint. Tailscale gebruikt de control plane en DERP-connectieopbouw om actuele endpointinformatie uit te wisselen. Daarna proberen de peers met outbound UDP en NAT traversal een direct pad te maken. Als dat niet lukt, blijft peer relay of DERP als fallback beschikbaar.

De data plane blijft met WireGuard end-to-end versleuteld. Een direct pad geeft meestal de beste performance. Een relay voegt een tussenpunt, latency en metadatazicht toe, maar kan de VPN-inhoud niet automatisch lezen.

De lokale netwerkbeheerders zien vooral buitenste IP's, poorten, timing en volume. Het Debian-endpoint ziet op `tailscale0` de ontsleutelde HTTP-request. De tailnetbeheerder ziet identity-, device- en policyinformatie. Dit toont dat versleutelde inhoud en zichtbare metadata verschillende zaken zijn.

Eindzin:

> De overlay blijft logisch stabiel, maar het underlaypad, de NAT mapping, het connection type, de performance en de zichtbare metadata worden bij elke netwerkomgeving opnieuw bepaald.
