---
marp: true
theme: default
paginate: true
size: 16:9
footer: Enterprise Networks - Hoofdstuk 6
style: |
  :root {
    --ink: #17212b;
    --blue: #153b5b;
    --cyan: #008f95;
    --sky: #dff3f4;
    --paper: #f7f8f6;
    --muted: #5d6972;
    --red: #b42318;
    --green: #16794b;
    --amber: #b66a00;
  }
  section {
    font-family: Aptos, "Segoe UI", sans-serif;
    color: var(--ink);
    background: white;
    padding: 46px 62px;
    font-size: 27px;
    overflow: hidden;
  }
  h1, h2 { color: var(--blue); }
  h1 { font-size: 1.66em; margin-bottom: 0.45em; }
  h2 { font-size: 1.18em; margin-bottom: 0.45em; }
  h3 { color: var(--cyan); margin: 0 0 0.35em; }
  p, li { line-height: 1.24; }
  strong { color: var(--blue); }
  blockquote {
    border-left: 8px solid var(--cyan);
    background: var(--sky);
    padding: 0.45em 0.8em;
    color: var(--blue);
  }
  table {
    width: 100%;
    font-size: 0.61em;
    border-collapse: collapse;
  }
  th {
    background: var(--blue);
    color: white;
    border: 1px solid #bcc8cf;
  }
  td {
    border: 1px solid #bcc8cf;
  }
  tr:nth-child(even) td { background: var(--paper); }
  td, th { padding: 0.32em 0.45em; }
  code {
    background: #edf1f4;
    color: #8a1c1c;
    border-radius: 4px;
    padding: 0.04em 0.22em;
    overflow-wrap: anywhere;
  }
  pre {
    background: #17212b;
    color: #f5f7f8;
    border-radius: 8px;
    padding: 0.62em 0.78em;
    font-size: 0.58em;
    line-height: 1.18;
    white-space: pre-wrap;
  }
  pre code {
    background: transparent;
    color: inherit;
    padding: 0;
    border-radius: 0;
  }
  pre code span {
    color: #f5f7f8 !important;
  }
  section.title {
    background: linear-gradient(135deg, var(--blue) 0%, #245b7c 68%, var(--cyan) 100%);
    color: white;
  }
  section.title h1,
  section.title h2,
  section.title strong { color: white; }
  section.title footer { color: rgba(255,255,255,.78); }
  section.divider {
    background: var(--blue);
    color: white;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  section.divider h1,
  section.divider h2 { color: white; }
  section.question { background: var(--paper); }
  section.question h1,
  section.question h2 { color: var(--cyan); }
  .columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
  }
  .columns-40-60 {
    display: grid;
    grid-template-columns: 0.8fr 1.2fr;
    gap: 30px;
  }
  .three {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }
  .four {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
  }
  .card {
    background: var(--paper);
    border-top: 5px solid var(--cyan);
    padding: 13px 17px;
  }
  .card p { margin: 0.2em 0; }
  .bad { color: var(--red); }
  .good { color: var(--green); }
  .warn { color: var(--amber); }
  .small { font-size: 0.72em; }
  .tiny { font-size: 0.61em; }
  .muted { color: var(--muted); }
  .big-claim {
    font-size: 1.48em;
    line-height: 1.18;
    color: var(--blue);
    font-weight: 700;
  }
  .pipeline {
    display: grid;
    grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr auto 1fr;
    align-items: stretch;
    gap: 9px;
    margin-top: 0.75em;
  }
  .pipeline .node {
    background: var(--paper);
    border-bottom: 5px solid var(--cyan);
    padding: 12px 9px;
    text-align: center;
    font-size: 0.61em;
  }
  .pipeline .arrow {
    align-self: center;
    color: var(--cyan);
    font-size: 1.2em;
    font-weight: 700;
  }
  .steps {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
  }
  .step {
    min-height: 94px;
    padding: 10px 12px;
    background: var(--paper);
    border-bottom: 5px solid var(--cyan);
    font-size: 0.64em;
  }
  .step strong { display: block; font-size: 1.15em; margin-bottom: 0.25em; }
  .tag {
    display: inline-block;
    background: var(--sky);
    color: var(--blue);
    padding: 0.16em 0.5em;
    margin: 0.1em 0.12em;
    font-size: 0.72em;
    font-weight: 700;
  }
  .diagram {
    background: var(--paper);
    border-left: 8px solid var(--cyan);
    padding: 18px 22px;
    font-size: 0.62em;
    white-space: pre;
    font-family: Consolas, "Cascadia Mono", monospace;
  }
---

<!-- _class: title -->
<!-- _paginate: false -->
<!-- _footer: "" -->

# Enterprise Networks

## Hoofdstuk 6 - VPN policy en routed access

**Van "de tunnel werkt" naar aantoonbaar beperkte toegang**

---

# BluePeak werkt remote

Een medewerker verbindt via Tailscale met het bedrijfsnetwerk.

Vandaag moet die medewerker:

<span class="tag">VM1 HTTP testen</span>
<span class="tag">NetBox via HTTPS openen</span>
<span class="tag">interne DNS gebruiken</span>

Maar niet:

<span class="tag">alle VM-poorten bereiken</span>
<span class="tag">SSH naar NetBox krijgen</span>
<span class="tag">het hele labnet scannen</span>
<span class="tag">oude testdevices laten staan</span>

> Een VPN die werkt, is nog geen goed toegangsontwerp.

---

<!-- _class: question -->

## Startvraag

# Je `curl` naar een server werkt.

# Wat heb je dan nog niet bewezen?

Denk aan: **wie**, **welk device**, **welke dienst**, **welke poort** en **welke verboden flows**.

---

# Leerdoelen

Na deze les kan je:

1. bereikbaarheid en autorisatie van elkaar onderscheiden;
2. klassieke brede VPN-toegang vergelijken met identity-aware access;
3. users, groups, autogroups, devices en tags correct plaatsen;
4. ACL's lezen als bron, bestemming, protocol en poort;
5. direct device access en routed access ontwerpen en controleren;
6. positieve en negatieve tests gebruiken voor policy, SSH, routes en DNS.

---

# Connectiviteit is alleen de eerste helft

| Vraag | Voorbeeld | Bewijst vooral |
|---|---|---|
| Kan ik het doel bereiken? | `curl http://vm1` | er bestaat een bruikbaar pad |
| Mag deze flow werken? | member -> `tag:webserver:80` | policy staat deze dienst toe |
| Blijft andere toegang dicht? | `nc -vz vm1 443` faalt | least privilege wordt begrensd |
| Is dit lifecycle-proof? | key ingetrokken, node verwijderd | toegang volgt beheerproces |

> De enterprisevraag is niet: "ben ik binnen?", maar: "mag precies deze flow?"

---

# De rode draad van Ch6

<div class="pipeline">
  <div class="node"><strong>Behoefte</strong><br>welke bedrijfsflow?</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Identity</strong><br>user, group of tag?</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Route</strong><br>direct of via subnet router?</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Policy</strong><br>protocol en poort</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Bewijs</strong><br>allow + deny + audit</div>
</div>

Een succesvolle test zonder vooraf vastgelegde verwachting is vooral toeval met screenshots.

---

# Klassieke VPN-reflex versus identity-aware access

| Brede VPN-reflex | Identity-aware reflex |
|---|---|
| VPN actief betekent intern | VPN actief levert alleen een mogelijk datapad |
| subnet of VPN-pool bepaalt vertrouwen | user, device en rol leveren policycontext |
| toegang tot een netwerksegment | toegang tot specifieke resource of service |
| positieve test is voldoende | positieve en negatieve tests zijn nodig |
| tijdelijke brede regel blijft staan | afwijking krijgt eigenaar en einddatum |

**Tailscale geeft policybouwstenen. De ontwerper bepaalt of die werkelijk least privilege afdwingen.**

---

# Labtopologie

<div class="diagram">                    persoonlijke tailnet

  Laptop -----------------------> VM1
  user-owned     direct access    tag:student-vm
  testclient                      tag:webserver
                                  HTTP TCP/80
        |
        | routed access
        v
  VM2 subnet router
  tag:subnet-router
  route 10.20.0.0/16
        |
        v
  intern labnet
  10.20.0.1    DNS voor voltlab.lan
  10.20.10.4   NetBox via HTTPS</div>

VM1 en VM2 krijgen hun gewone lab-IP via DHCP: dat zijn meetwaarden.

---

# Direct device access en routed access

| Kenmerk | Direct device access | Routed access |
|---|---|---|
| Tailscale op eindbestemming | ja | niet noodzakelijk |
| Voorbeeld | `tag:webserver` | `10.20.10.4` |
| Policydoel | device-identiteit of tag | IP-adres, hostalias of subnet |
| Gateway | niet nodig | VM2 als subnet router |
| Extra foutbronnen | dienst, hostfirewall | forwarding, route, SNAT, return path |
| Naamresolutie | MagicDNS | Split DNS |

**Een route naar een subnet is nog geen toelating tot elke host in dat subnet.**

---

# Verwachte flows eerst vastleggen

| Bron | Doel | Service | Verwacht | Reden |
|---|---|---|:---:|---|
| laptop | VM1 | HTTP TCP/80 | allow | webdienst testen |
| laptop | VM1 | HTTPS TCP/443 | deny | niet vereist |
| laptop | NetBox | HTTPS TCP/443 | allow | routed access testen |
| laptop | NetBox | SSH TCP/22 | deny | geen beheerrecht |
| laptop | DNS-server | DNS UDP/53 | allow | interne zone oplossen |
| laptop | DNS-server | SSH TCP/22 | deny | resolver is geen beheerdoel |

> Als je verwachtingen pas achteraf bedenkt, pas je ze gemakkelijk aan het toevallige resultaat aan.

---

# De policy file is meer dan firewallregels

| Sectie | Functie |
|---|---|
| `groups` | users groeperen onder een rolnaam |
| `hosts` | leesbare alias voor IP-adres of subnet |
| `tagOwners` | bepalen wie device-tags mag toekennen |
| `acls` | oorspronkelijke netwerktoegangssyntaxis |
| `grants` | moderne netwerk- en applicatiecapabilities |
| `ssh` | Tailscale SSH-bron, doel en lokale user |
| `autoApprovers` | route- of exit-nodegoedkeuring automatiseren |
| `tests` / `sshTests` | policyverwachtingen als asserties |

De policy combineert **naamgeving, identiteit, roltoekenning, toegang en bewijs**.

---

# De standaard-policyvalkuil

Een nieuwe of nooit aangepaste tailnet kan brede connectiviteit toelaten.

| Situatie | Praktisch gevolg |
|---|---|
| policy nooit aangepast | standaard allow-all kan gelden |
| expliciete `acls` of `grants` aanwezig | alleen gematchte flows worden toegestaan |
| expliciete lege access-controlsectie | geen netwerkflows via die policylaag |

Typische fout:

> "Ik verwijderde de allow-regel, dus het is zeker geblokkeerd."

Controleer de **volledige effectieve policy** en voer een negatieve runtime-test uit.

---

# ACL's en grants

| Eigenschap | ACL's | Grants |
|---|---|---|
| Rol | oorspronkelijke syntaxis | aanbevolen voor nieuwe policy's |
| Netwerktoegang | `src`, `dst`, optioneel `proto` | `src`, `dst`, `ip` |
| Applicatiecapabilities | niet voorzien | mogelijk via `app` |
| Servicevoorbeeld | `tag:webserver:80` | `ip: ["tcp:80"]` |
| Ch6-workshop | gebruikt ACL's | conceptueel vergelijken |

ACL's en grants zijn **additief**: een flow die door één passende regel wordt toegestaan, blijft toegestaan.

---

# Vier eigenschappen van netwerkpolicy

| Eigenschap | Betekenis | Gevolg |
|---|---|---|
| deny by default na expliciete policy | niet-gematchte flows worden geblokkeerd | je schrijft vooral allow-regels |
| directioneel | `A -> B` geeft geen initiatierecht `B -> A` | server mag niet automatisch terug starten |
| stateful antwoordverkeer | responses op toegelaten sessies mogen terug | geen spiegelregel nodig |
| lokaal afgedwongen | devices handhaven packet filters | payload hoeft niet langs control plane |

```text
laptop start TCP/80 naar VM1 -> policy controleert nieuwe flow
VM1 antwoordt binnen sessie  -> hoort bij toegelaten flow
VM1 start nieuwe flow        -> aparte toelating nodig
```

---

<!-- _class: question -->

## Wat kan hier misgaan?

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "dst": ["tag:webserver:80"]
}
```

Een student zegt: **"VM1 is nu veilig afgeschermd."**

Welke controles ontbreken nog?

Hints: volledige policy, andere tags, TCP/443, TCP/22, policytests, runtimegedrag.

---

# Users, groups en autogroups

| Selector | Betekenis | Sterkte | Aandachtspunt |
|---|---|---|---|
| user | één menselijke identiteit | precies | minder schaalbaar |
| `group:students` | gedefinieerde rolgroep | centraal beheer | groep is geen reden op zich |
| `autogroup:member` | directe tailnetleden | handig in persoonlijk lab | te breed in gedeelde tailnet |
| `autogroup:admin` | users met adminrol | bruikbaar voor labtag owners | adminrol is krachtig |
| `*` | wildcard | snel voor diagnose | bijna altijd te breed |

**Gebruik alleen een selector waarvan je de scope kan uitleggen.**

---

# User-owned versus tagged device

<div class="columns">
<div class="card">

### User-owned

- gekoppeld aan een persoon;
- past bij laptop of werkplek;
- policy volgt user of group;
- lifecycle volgt de medewerker.

</div>
<div class="card">

### Tagged

- gekoppeld aan een rol;
- past bij server, router of workload;
- policy volgt `tag:...`;
- lifecycle volgt de dienst.

</div>
</div>

```text
fout:  server is van Alice én tag:webserver
juist: server handelt als tagidentiteit; Alice kan tagbeheerder zijn
```

---

# Meerdere tags tellen samen

VM1 kan tegelijk hebben:

<span class="tag">tag:student-vm</span>
<span class="tag">tag:webserver</span>
<span class="tag">tag:ssh-server</span>

| Regel | Effect op VM1 |
|---|---|
| HTTP naar `tag:webserver` | VM1 ontvangt HTTP-toegang |
| SSH naar `tag:ssh-server` | VM1 valt onder SSH-doelrol |
| monitoring naar `tag:student-vm` | VM1 ontvangt ook die algemene flow |

> Een extra tag beperkt niet automatisch. Ze kan net bijkomende toegangsregels activeren.

---

# Tag owners zijn een securitygrens

```json
"tagOwners": {
  "tag:student-vm": ["autogroup:admin"],
  "tag:webserver": ["autogroup:admin"],
  "tag:ssh-server": ["autogroup:admin"],
  "tag:subnet-router": ["autogroup:admin"]
}
```

Wie een tag mag toekennen, bepaalt indirect welke identity en toegangsrechten een device kan krijgen.

| Foute keuze | Risico |
|---|---|
| alle members mogen servertags gebruiken | elke user kan een device in serverrol plaatsen |
| reusable provisioningkey zonder begrenzing | meerdere ongewenste nodes met tag |
| persoonlijke admin blijft owner | mover behoudt indirecte macht |

---

# Auth keys: onboarding zonder browserlogin

Auth keys passen bij headless servers, VM-templates, containers en automatisatie.

| Eigenschap | Betekenis | Risico |
|---|---|---|
| one-off | één registratie | lek vóór gebruik geeft één ongewenste node |
| reusable | meerdere registraties | diefstal kan vlootuitrol misbruiken |
| ephemeral | tijdelijke node wordt opgeruimd | niet voor blijvende serveridentiteit |
| pre-approved | omzeilt device approval | provisioningpad krijgt extra macht |
| tagged | node neemt tagidentiteit aan | verkeerde tag vergroot privileges |

**Een auth key is een credential. Niet in code, screenshots, history of verslag.**

---

# Anatomie van een ACL

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "proto": "tcp",
  "dst": ["tag:webserver:80"]
}
```

| Veld | Betekenis | Vraag |
|---|---|---|
| `action` | beslissing bij match | wordt deze flow toegestaan? |
| `src` | startende identiteit of bronset | wie initieert? |
| `proto` | IP-protocol | TCP, UDP of iets anders? |
| `dst` | doel en poort | welke resource en service? |

Lees dit als zin: **members mogen TCP/80 starten naar webservers**.

---

# Van behoefte naar policy

Mensentaal:

> De laptop van een tailnetlid moet de HTTP-dienst op VM1 kunnen testen.

| Beslissing | Keuze | Waarom? |
|---|---|---|
| bron | `autogroup:member` | persoonlijk lab |
| bestemming | `tag:webserver` | rol blijft stabiel |
| protocol | TCP | HTTP gebruikt TCP |
| poort | 80 | alleen webdienst nodig |

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "proto": "tcp",
  "dst": ["tag:webserver:80"]
}
```

---

# Deny by omission en brede regels

Binnen een expliciete deny-by-default-policy geldt:

```text
allow TCP/80 naar tag:webserver
geen allow voor TCP/443
gevolg: TCP/443 is niet toegestaan
```

Maar:

```json
{
  "action": "accept",
  "src": ["*"],
  "dst": ["*:*"]
}
```

maakt fijnere regels ernaast bijna irrelevant.

> Een brede allow wordt niet veilig door daarnaast ook een smalle regel te schrijven.

---

# Policytests en runtime-tests

| Testniveau | Voorbeeld | Bewijst |
|---|---|---|
| policytest | `tests` in de policy file | policy-engine verwacht allow of deny |
| runtime-test | `curl`, `nc`, `ssh`, `nslookup` | route, policy, host, DNS en service samen |

Een policytest start geen HTTP-sessie.

Een runtime-test beschermt niet automatisch tegen regressies bij de volgende policywijziging.

**Sterk bewijs gebruikt beide.**

---

<!-- _class: question -->

## Checkpoint - policy redeneren

Je wil alleen NetBox via HTTPS toelaten.

Een student stelt voor:

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "dst": ["10.20.0.0/16:*"]
}
```

Welke gewenste flow werkt hierdoor?

Welke ongewenste flows werken waarschijnlijk ook?

---

# Directe HTTP-toegang naar VM1

VM1 is zelf een Tailscale-device en krijgt `tag:webserver`.

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "proto": "tcp",
  "dst": ["tag:webserver:80"]
}
```

Test niet alleen de allow:

| Test | Verwacht | Bewijst |
|---|:---:|---|
| `curl -I http://<vm1-tailscale-ip>` | allow | HTTP-flow werkt |
| `nc -vz <vm1-tailscale-ip> 443` | deny | HTTPS is niet mee open |
| `nc -vz <vm1-tailscale-ip> 22` | deny | SSH is niet impliciet open |

---

# Drie SSH-begrippen uit elkaar houden

| Begrip | Wat gebeurt er? |
|---|---|
| klassieke SSH buiten Tailscale | OpenSSH-client bereikt `sshd` via LAN- of publiek IP |
| OpenSSH over Tailscale | gewone SSH-client bereikt `sshd` via Tailscale-IP |
| Tailscale SSH | `tailscaled` neemt inkomend TCP/22 op Tailscale-IP over |

Tailscale SSH gebruikt tailnetidentiteit voor authenticatie en autorisatie.

Maar het blijft verkeer naar **TCP/22**.

---

# Tailscale SSH heeft twee policylagen

Voor een toegelaten Tailscale SSH-sessie:

```text
1. Tailscale SSH staat aan op de bestemming
2. netwerkpolicy laat bron -> bestemming TCP/22 toe
3. ssh-policy laat bron -> bestemming -> lokale user toe
```

<div class="columns">
<div>

### Netwerklaag

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "proto": "tcp",
  "dst": ["tag:student-vm:22"]
}
```

</div>
<div>

### SSH-laag

```json
"ssh": [{
  "action": "accept",
  "src": ["autogroup:member"],
  "dst": ["tag:student-vm"],
  "users": ["debian"]
}]
```

</div>
</div>

---

# Correcte SSH-testmatrix

| Test | Verwacht | Wat bewijst dit? |
|---|---|---|
| TCP/22-regel ontbreekt | sessie faalt | netwerkpoort is eerste gate |
| TCP/22 toegestaan, geen SSH-regel | login faalt | netwerktoegang is geen SSH-autorisatie |
| TCP/22 + user `debian` toegestaan | login werkt | beide policylagen kloppen |
| aanmelden als `root` | faalt | lokale userscope is beperkt |
| via gewoon lab-IP | apart gedrag | dit pad valt buiten tailnetpolicy |

Een `nc -vz <tailscale-ip> 22` bewijst geen loginrecht.

---

<!-- _class: question -->

## Wat kan hier misgaan?

**Symptoom:** `tailscale ssh debian@vm1` faalt.

Mogelijke oorzaken:

- Tailscale SSH staat niet aan op VM1;
- VM1 heeft niet de verwachte tag;
- TCP/22 ontbreekt in netwerkpolicy;
- `ssh`-sectie laat `debian` niet toe;
- lokale user `debian` bestaat niet of is niet bruikbaar.

**In welke volgorde controleer je dit zonder meteen `*:*` toe te voegen?**

---

# Wat doet een subnet router?

Een subnet router is een Tailscale-device dat verkeer doorstuurt naar een netwerk waar de eindbestemming zelf geen Tailscale draait.

<div class="diagram">Laptop 100.x.y.z
      |
      | versleutelde tailnetflow
      v
VM2 subnet router
      |
      | intern labnet 10.20.0.0/16
      v
NetBox 10.20.10.4</div>

Nuttig voor legacyservers, printers, netwerktoestellen of gefaseerde migratie.

Risico: één router kan potentieel veel adressen achter zich bereikbaar maken.

---

# Voorwaarden voor een routed flow

| Voorwaarde | Functie | Typische fout |
|---|---|---|
| Tailscale op VM2 | router is peer | node offline of verkeerd aangemeld |
| IP forwarding | OS stuurt pakketten door | niet actief of niet persistent |
| routeadvertentie | prefix wordt aangeboden | verkeerd prefix |
| routegoedkeuring | beheerder aanvaardt route | route blijft pending |
| routeacceptatie | client gebruikt route | Linux accepteert niet automatisch |
| access policy | concrete flow is toegestaan | route bestaat, packet filter blokkeert |
| firewall / return path | antwoord komt terug | asymmetrische routing of blokkade |

---

# Adverteren, goedkeuren, accepteren

Op VM2:

```bash
sudo sysctl -w net.ipv4.ip_forward=1
sudo tailscale up --advertise-routes=10.20.0.0/16 --hostname=<VM2-NAME>
```

Daarna:

1. route goedkeuren in de Tailscale admin console;
2. controleren of de client de route gebruikt;
3. op Linux eventueel routes expliciet accepteren.

```bash
sudo tailscale set --accept-routes
```

**Routeadvertentie is geen access policy.**

---

# SNAT en return routing

Bij subnet routing moet het antwoord terug naar de client kunnen.

| Keuze | Wat ziet de interne host? | Aandachtspunt |
|---|---|---|
| SNAT aan | bron lijkt VM2 | eenvoudiger labrouting, minder zicht op echte client |
| SNAT uit | bron blijft tailnetclient | intern netwerk moet retourroute kennen |

In het lab maakt SNAT de routing eenvoudiger.

In productie is dit een bewuste ontwerpkeuze:

<span class="tag">logging</span>
<span class="tag">attributie</span>
<span class="tag">return path</span>
<span class="tag">firewallbeleid</span>

---

# Breed routeprefix, smalle policy

VM2 adverteert `10.20.0.0/16` omdat DNS en NetBox in dat labnet zitten.

Dat betekent niet:

```text
student mag 10.20.0.0/16 op alle poorten gebruiken
```

Wel:

| Laag | Labkeuze |
|---|---|
| route | `10.20.0.0/16` via VM2 |
| NetBox-policy | alleen `10.20.10.4:443` via TCP |
| DNS-policy | alleen `10.20.0.1:53` via vereiste protocollen |
| overige hosts en poorten | geen allow |

---

# HTTPS naar NetBox beperken

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "proto": "tcp",
  "dst": ["10.20.10.4:443"]
}
```

Deze regel geeft geen toegang tot:

| Niet toegelaten | Waarom niet? |
|---|---|
| `10.20.10.4:22` | andere poort |
| `10.20.10.4:80` | andere poort |
| `10.20.10.5:443` | ander adres |
| VM2 op zijn Tailscale-IP | routerdevice is niet het routed doel-IP |
| volledig `10.20.0.0/16` | slechts één host is geselecteerd |

---

# Negatieve routed tests

| Test | Verwacht | Wat bewijst dit vooral? |
|---|:---:|---|
| `curl -kI https://10.20.10.4` | allow | route, TCP/443-policy en webdienst |
| `nc -vz 10.20.10.4 22` | deny | NetBox-managementpoort niet toegestaan |
| `nc -vz 10.20.10.4 80` | deny | alleen HTTPS is nodig |
| `nc -vz 10.20.0.1 22` | deny | DNS-server is geen beheerdoel |

Een gefaalde `nc` bewijst niet alleen ACL-deny: poort gesloten of hostfirewall kan ook.

Combineer met policy preview, policytests en relevante logs.

---

# MagicDNS en Split DNS

| Vraag | MagicDNS | Split DNS |
|---|---|---|
| Welke namen? | tailnet-devices | records in gekozen interne zones |
| Voorbeeld | `s01-ch6-web-01` | `netbox.voltlab.lan` |
| Externe resolver nodig? | niet voor normale device-namen | ja, `10.20.0.1` |
| Routed access nodig? | niet voor directe tailnetdevices | wel als resolver achter VM2 staat |
| Typische fout | verkeerde machinenaam | route, ACL, resolver of zone fout |

**MagicDNS benoemt tailnet-devices. Split DNS stuurt geselecteerde zones naar een resolver.**

---

# DNS heeft zelf een pad en policy nodig

DNS-configuratie creëert geen route en geen access-controltoelating.

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "proto": "udp",
  "dst": ["10.20.0.1:53"]
}
```

Afhankelijk van requirements kan TCP/53 ook nodig zijn.

```text
restricted zone -> resolver 10.20.0.1
route naar resolver via VM2
policy laat DNS toe
resolver kent netbox.voltlab.lan
```

---

# Test DNS pas nadat IP werkt

Gebruik deze volgorde:

<div class="steps">
  <div class="step"><strong>1</strong>`curl -kI https://10.20.10.4`<br>route, policy en service</div>
  <div class="step"><strong>2</strong>`nslookup netbox.voltlab.lan`<br>Split DNS en resolverpad</div>
  <div class="step"><strong>3</strong>`curl -kI https://netbox.voltlab.lan`<br>naam in applicatieflow</div>
  <div class="step"><strong>4</strong>publieke naam oplossen<br>split blijft beperkt</div>
</div>

Als stap 1 faalt, is DNS wijzigen meestal ruis.

Als stap 1 werkt en stap 2 faalt, kijk je naar DNS-configuratie, UDP/TCP/53-policy en resolverbereikbaarheid.

---

# Subnet router versus exit node

| Eigenschap | Subnet router | Exit node |
|---|---|---|
| Doel | intern subnet bereikbaar maken | internet/default route via andere locatie |
| Typische routes | `10.20.0.0/16` | `0.0.0.0/0`, `::/0` |
| Clientgedrag | route volgens routing table | client kiest exit node |
| Hoofdtest | interne host/service werkt | publiek bron-IP verandert |
| Belangrijk risico | te brede interne ontsluiting | privacy, capaciteit, egresscontrole |

NetBox heeft geen exit node nodig. De route naar `10.20.0.0/16` via VM2 volstaat.

---

# Eén flow passeert meerdere controlelagen

<div class="pipeline">
  <div class="node"><strong>Identity</strong><br>user, group, tag</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Route</strong><br>peerpad of subnet</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Policy</strong><br>allow of deny?</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Host/service</strong><br>firewall en socket</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Applicatie</strong><br>login en rechten</div>
</div>

Een Tailscale ACL vervangt geen autorisatie binnen NetBox.

TCP/443 bereikbaar maken betekent alleen dat de HTTPS-service bereikbaar is.

---

# Foutscenario's lokaliseren

| Symptoom | Mogelijke laag | Eerste controle |
|---|---|---|
| Tailscale-IP VM1 onbereikbaar | peerstatus of policy | `tailscale status`, policy preview |
| VM1 pingt, HTTP faalt | ACL, firewall, service | TCP/80-policy, `ss`, `curl` |
| route zichtbaar, NetBox faalt | ACL, forwarding, return path | test vanaf VM2, policy |
| HTTPS via IP werkt, via naam niet | DNS | restricted zone, query naar resolver |
| TCP/22 bereikbaar, SSH-login faalt | SSH-policy of lokale user | `ssh`-regel, OS-user |
| user kan openen maar niet beheren | applicatieautorisatie | applicatierollen |

Typische valkuil: bij elk probleem tijdelijk `*:*` toelaten.

---

# Baseline vóór wijziging

Meet en noteer:

| Baseline | Waarom? |
|---|---|
| devices en identities | toont wie werkelijk deelneemt |
| Tailscale-IP's | koppelt tests aan endpoints |
| VM1- en VM2-lab-IP | onderscheidt overlaypad en lokaal pad |
| bestaande policy | oude brede allow wordt zichtbaar |
| route- en DNS-status | maakt latere wijzigingen vergelijkbaar |
| luisterende diensten | voorkomt foutieve ACL-conclusie |

> Zonder baseline weet je niet of je iets hebt opgelost of gewoon iets anders hebt geraakt.

---

# Test van laag naar gebruikersflow

<div class="steps">
  <div class="step"><strong>1</strong>Identity, namen en tags controleren</div>
  <div class="step"><strong>2</strong>Peers online en directe HTTP naar VM1 testen</div>
  <div class="step"><strong>3</strong>Onnodige VM1-poorten negatief testen</div>
  <div class="step"><strong>4</strong>Tailscale SSH met beide policylagen testen</div>
  <div class="step"><strong>5</strong>Forwarding, routeadvertentie en routeacceptatie controleren</div>
  <div class="step"><strong>6</strong>NetBox eerst via IP en TCP/443 testen</div>
  <div class="step"><strong>7</strong>Ongewenste routed poorten testen</div>
  <div class="step"><strong>8</strong>Split DNS en cleanup valideren</div>
</div>

---

# Wat noteer je per test?

```text
Test-ID: T6
Bronidentity: <student-login-email>
Brondevice: <laptop-name>
Bestemming: 10.20.10.4
Protocol/poort: TCP/22
Verwachting: deny
Werkelijk: timeout / refused / policymelding
Aanvullend bewijs: policytest deny + relevante policyregel
Conclusie: geen allow voor NetBox-managementpoort
```

Een negatieve test is sterk wanneer je zowel het verwachte blokkeermechanisme als het waargenomen resultaat kan aanwijzen.

---

# Troubleshooting zonder policy te verbreden

Gebruik één hypothese per stap:

1. Is de bronidentity wat ik denk?
2. Selecteert de policy het juiste doel?
3. Bestaat het peerpad of de subnetroute?
4. Laat policy protocol en poort toe?
5. Forwardt de router?
6. Kan de router de bestemming bereiken?
7. Komt antwoordverkeer terug?
8. Luistert de dienst?
9. Is DNS pas daarna correct?

> Verander één relevante variabele, herhaal dezelfde test en herstel tijdelijke wijzigingen.

---

# Audit, logs, privacy en secrets

| Bewijsbron | Sterkte |
|---|---|
| policytest | verwachte beslissing door policy-engine |
| runtime negatieve test | werkelijk clientgedrag |
| host- of firewalllog | waar pakket werd geweigerd of ontvangen |
| configuratie-auditlog | wie policy, route, DNS, tag of key wijzigde |
| netwerkflowlog | succesvolle verkeersflow en metadata, indien beschikbaar |

Niet opnemen in verslag:

<span class="tag">auth key</span>
<span class="tag">API-token</span>
<span class="tag">loginlink</span>
<span class="tag">recovery code</span>
<span class="tag">wachtwoord</span>
<span class="tag">private key</span>

---

# Lifecycle eindigt niet na een werkende test

| Fase | Beheeractie | Bewijs |
|---|---|---|
| aanvraag | doel en vereiste flows vastleggen | labplan of ticket |
| onboarding | identity, naam, tags en keytype kiezen | inventaris klopt |
| gebruik | policy en routes toepassen | allow- en deny-tests |
| review | noodzaak en last seen controleren | reviewconclusie |
| incident | key intrekken of device isoleren | toegang stopt |
| offboarding | node, routes en tijdelijke policy verwijderen | negatieve hertest |

Een auth key intrekken is niet hetzelfde als een al geregistreerde node verwijderen.

---

# Labkeuzes en productieontwerp

| Thema | Labkeuze | Productieontwerp |
|---|---|---|
| rollen | student is member en admin | gescheiden owner, admin, auditor, user |
| bronselector | `autogroup:member` | functiegerichte groups en posture |
| tag owners | `autogroup:admin` | beperkte beheergroep of provisioningidentity |
| auth key | korte one-off key | secret store en gecontroleerde uitgifte |
| subnet router | één VM2 | redundantie, monitoring, capaciteit |
| DNS | één restricted nameserver | redundante resolvers |
| policybeheer | webeditor | peer review, versiebeheer, tests |
| cleanup | na workshop | geautomatiseerde lifecycle |

De workshop toont de toegangslogica; productie voegt governance en beschikbaarheid toe.

---

<!-- _class: question -->

## Mini-case

Een policytest voor `10.20.10.4:443` slaagt, maar:

```bash
curl -kI https://10.20.10.4
```

faalt vanaf de laptop.

Welke lagen onderzoek je nu?

- policy-engine?
- route op de client?
- VM2 forwarding?
- test vanaf VM2 naar NetBox?
- host- of LAN-firewall?
- return path of SNAT?

Wat mag je nog niet concluderen?

---

# Van theorie naar praktijk

In de workshop behandel je je persoonlijke tailnet als een kleine organisatie.

Je zal:

- laptop, VM1 en VM2 inventariseren;
- VM1 als tagged server onboarden met een auth key;
- directe HTTP-toegang toelaten en andere poorten blokkeren;
- Tailscale SSH onderscheiden van gewone SSH;
- VM2 als subnet router gebruiken;
- NetBox alleen via HTTPS bereikbaar maken;
- Split DNS voor `netbox.voltlab.lan` testen;
- audit en cleanup uitvoeren zonder secrets te lekken.

---

<!-- _class: question -->

## Voorbereidende case

BluePeak heeft:

- een werkende tailnet;
- VM1 met `tag:webserver`;
- VM2 die `10.20.0.0/16` adverteert;
- NetBox op `10.20.10.4`;
- een policy met één brede regel: `autogroup:member -> 10.20.0.0/16:*`.

**Welke minimale regels en tests stel je voor om dit least privilege te maken?**

Geef minstens één allow-test en twee deny-tests.

---

# Wat moet je onthouden?

1. VPN-connectiviteit is een datapad, geen blanco toegangsrecht.
2. Dezelfde tailnet betekent niet dezelfde trust of dezelfde rechten.
3. Tags geven servers en routers een rolidentiteit; tag owners bepalen wie die rol mag uitdelen.
4. Een subnet route ontsluit een pad; policy begrenst welke diensten bruikbaar zijn.
5. Professionele toegang bewijs je met identity, route, policy, positieve tests, negatieve tests, audit en cleanup.
