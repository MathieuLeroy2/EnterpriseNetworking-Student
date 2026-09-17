# Workshop 8 - Interne applicaties publiceren via Traefik

## 1. Situering

In deze workshop bouw je stap voor stap een reverse-proxyomgeving met **Traefik**.

Je krijgt niet meteen een volledig afgewerkte configuratie.

Je start met:

- een lege Traefik-basis in `docker-compose.yml`;
- een lege dynamic config in `traefik/dynamic.yml`;
- drie mappen met eenvoudige webpagina's.

Daarna voeg je telkens zelf een onderdeel toe:

1. Traefik starten;
2. intranet-backend toevoegen;
3. intranet-router en service toevoegen;
4. helpdesk toevoegen;
5. statuspagina toevoegen;
6. security headers toevoegen;
7. positieve en negatieve tests uitvoeren.

Belangrijk:

> Een applicatie die via de proxy werkt, is pas correct gepubliceerd als de backend niet rechtstreeks via een aparte hostpoort bereikbaar is.

---

## 2. Scenario

**BluePeak Services** heeft drie interne webapplicaties:

| Applicatie | Doelgroep | Gewenste hostname |
|---|---|---|
| Intranet | medewerkers | `intranet.bluepeak.test` |
| Helpdesk | medewerkers en IT | `helpdesk.bluepeak.test` |
| Statuspagina | IT en operations | `status.bluepeak.test` |

De organisatie wil niet dat elke applicatie een eigen publieke poort krijgt.

Alle webtoegang moet via Traefik lopen.

De centrale onderzoeksvraag is:

> Hoe bouw je een reverse-proxyconfiguratie op zonder per ongeluk de interne backends rechtstreeks te publiceren?

---

## 3. Beginsituatie

Werk in:

```text
Ch8/workshop/configs/student/reverse-proxy-lab
```

Je krijgt:

| Bestand of map | Doel |
|---|---|
| `docker-compose.yml` | starterbestand met Traefik |
| `traefik/dynamic.yml` | lege Traefik dynamic config |
| `sites/intranet/index.html` | demo-intranet |
| `sites/helpdesk/index.html` | demo-helpdesk |
| `sites/status/index.html` | demo-statuspagina |

De starterconfig bevat bewust nog geen backendservices en geen routes.

---

## 4. Doelen

Na deze workshop kan je:

1. een Traefik reverse proxy starten met Docker Compose;
2. het verschil uitleggen tussen static config en dynamic config;
3. een backendcontainer toevoegen zonder hostpoort;
4. een Traefik router schrijven met een `Host(...)` rule;
5. een Traefik service koppelen aan een interne backend-URL;
6. meerdere hostnames via dezelfde proxy publiceren;
7. security headers toevoegen via middleware;
8. aantonen dat directe backendpoorten niet gepubliceerd zijn;
9. proxylogs en dashboard gebruiken bij troubleshooting;
10. een backendfout herkennen als proxy-naar-backendprobleem;
11. een firewallvoorstel schrijven voor productie.

---

## 5. Benodigdheden

Je hebt nodig:

- Docker Desktop of Docker Engine;
- Docker Compose;
- terminal;
- browser;
- `curl.exe`;
- rechten om tijdelijk je lokale hosts file aan te passen, of een alternatief dat de docent voorziet.

---

## 6. Traefik: static config en dynamic config

Traefik gebruikt in deze workshop twee soorten configuratie.

### Static config

De static config bepaalt hoe Traefik zelf start.

In deze workshop staat die in `docker-compose.yml`, onder `command`.

Voorbeelden:

```text
--entrypoints.web.address=:80
--providers.file.filename=/etc/traefik/dynamic.yml
--api.dashboard=true
--accesslog=true
```

Deze instellingen zeggen:

- Traefik luistert intern op poort 80;
- Traefik leest dynamic config uit `dynamic.yml`;
- het dashboard staat aan;
- access logs staan aan.

### Dynamic config

De dynamic config bepaalt welke webapplicaties gepubliceerd worden.

Die staat in:

```text
traefik/dynamic.yml
```

Daarin definieer je:

| Onderdeel | Vraag |
|---|---|
| Router | Welke aanvraag matcht? |
| Rule | Welke hostname hoort erbij? |
| Service | Naar welke backend gaat het verkeer? |
| Middleware | Welke extra verwerking gebeurt onderweg? |

Kernzin:

> `docker-compose.yml` start de omgeving. `dynamic.yml` beschrijft hoe Traefik verkeer naar applicaties routeert.

---

## 7. Stap 1: start alleen Traefik

Bekijk eerst `docker-compose.yml`.

In de beginsituatie staat alleen de service `reverse-proxy` klaar.

Start:

```text
docker compose up -d
```

Controleer:

```text
docker compose ps
docker compose logs reverse-proxy
```

Open het dashboard:

```text
http://localhost:8088
```

Vul in:

| Controle | Verwacht | Werkelijk |
|---|---|---|
| Traefik-container draait | ja | ... |
| Web entrypoint | `8080:80` | ... |
| Dashboard | `8088:8080` | ... |
| Routers aanwezig | nog geen app-routers | ... |
| Services aanwezig | nog geen app-services | ... |

Controlepunt:

> Traefik draait, maar er zijn nog geen applicaties gepubliceerd.

---

## 8. Stap 2: voeg de intranet-backend toe

Nu voeg je de eerste interne applicatie toe.

Belangrijk:

> Een backendcontainer krijgt geen `ports:`-mapping. Anders publiceer je de applicatie rechtstreeks en omzeil je Traefik.

Voeg in `docker-compose.yml` onder `services:` een nieuwe service toe:

```yaml
  intranet:
    image: nginx:alpine
    container_name: ch8-intranet
    volumes:
      - ./sites/intranet:/usr/share/nginx/html:ro
    networks:
      - appnet
```

Start opnieuw:

```text
docker compose up -d
docker compose ps
```

Beantwoord:

- Draait de container `intranet`?
- Heeft `intranet` een hostpoort?
- Waarom is het goed dat `intranet` geen hostpoort heeft?
- Waarom kan Traefik de container toch bereiken?

Controlepunt:

> De intranet-backend bestaat nu, maar is nog niet via een hostname gepubliceerd.

---

## 9. Stap 3: publiceer intranet via dynamic.yml

Nu voeg je in `traefik/dynamic.yml` een router en service toe.

### 9.1 Wat moet er gebeuren?

Wanneer een client vraagt naar:

```text
intranet.bluepeak.test
```

moet Traefik doorsturen naar:

```text
http://intranet:80
```

Daarvoor heb je nodig:

| Onderdeel | Waarde |
|---|---|
| Router | `intranet` |
| Rule | `Host(\`intranet.bluepeak.test\`)` |
| Entrypoint | `web` |
| Service | `intranet` |
| Backend URL | `http://intranet:80` |

### 9.2 Voeg dit toe

Vervang de lege inhoud van `traefik/dynamic.yml` door:

```yaml
http:
  routers:
    intranet:
      rule: "Host(`intranet.bluepeak.test`)"
      entryPoints:
        - web
      service: intranet

  services:
    intranet:
      loadBalancer:
        servers:
          - url: "http://intranet:80"

  middlewares: {}
```

Traefik kijkt automatisch naar wijzigingen in `dynamic.yml`.

Test:

```text
curl.exe -I http://intranet.bluepeak.test:8080
```

Open ook in de browser:

```text
http://intranet.bluepeak.test:8080
```

Vul in:

| Test | Verwacht | Werkelijk |
|---|---|---|
| intranet via hostname | werkt | ... |
| dashboard router | `intranet` zichtbaar | ... |
| dashboard service | `intranet` zichtbaar | ... |

Controlepunt:

> De hostname wijst naar Traefik. Traefik gebruikt de router om de juiste backendservice te kiezen.

---

## 10. Stap 4: voeg helpdesk toe

Herhaal nu hetzelfde principe voor helpdesk.

### 10.1 Compose

Voeg in `docker-compose.yml` toe:

```yaml
  helpdesk:
    image: nginx:alpine
    container_name: ch8-helpdesk
    volumes:
      - ./sites/helpdesk:/usr/share/nginx/html:ro
    networks:
      - appnet
```

Start:

```text
docker compose up -d
```

### 10.2 Dynamic config

Voeg in `traefik/dynamic.yml` een router toe onder `routers:`:

```yaml
    helpdesk:
      rule: "Host(`helpdesk.bluepeak.test`)"
      entryPoints:
        - web
      service: helpdesk
```

Voeg onder `services:` toe:

```yaml
    helpdesk:
      loadBalancer:
        servers:
          - url: "http://helpdesk:80"
```

Test:

```text
curl.exe -I http://helpdesk.bluepeak.test:8080
```

Controlepunt:

> Je hebt nu twee applicaties op dezelfde proxypoort, gescheiden door hostname.

---

## 11. Stap 5: voeg status toe

Herhaal dezelfde aanpak voor de statuspagina.

### 11.1 Compose

Voeg in `docker-compose.yml` toe:

```yaml
  status:
    image: nginx:alpine
    container_name: ch8-status
    volumes:
      - ./sites/status:/usr/share/nginx/html:ro
    networks:
      - appnet
```

Start:

```text
docker compose up -d
```

### 11.2 Dynamic config

Voeg onder `routers:` toe:

```yaml
    status:
      rule: "Host(`status.bluepeak.test`)"
      entryPoints:
        - web
      service: status
```

Voeg onder `services:` toe:

```yaml
    status:
      loadBalancer:
        servers:
          - url: "http://status:80"
```

Test:

```text
curl.exe -I http://status.bluepeak.test:8080
```

Vul in:

| Hostname | Verwachte app | Werkelijk |
|---|---|---|
| `intranet.bluepeak.test` | intranet | ... |
| `helpdesk.bluepeak.test` | helpdesk | ... |
| `status.bluepeak.test` | status | ... |

---

## 12. Stap 6: voeg security headers toe

Een reverse proxy kan centraal headers toevoegen.

In Traefik doe je dit met een middleware.

Voeg onder `middlewares:` toe:

```yaml
    security-headers:
      headers:
        contentTypeNosniff: true
        frameDeny: true
        referrerPolicy: "strict-origin-when-cross-origin"
```

Koppel daarna elke router aan de middleware.

Voorbeeld:

```yaml
      middlewares:
        - security-headers
```

Doe dit voor:

- `intranet`;
- `helpdesk`;
- `status`.

Test:

```text
curl.exe -I http://intranet.bluepeak.test:8080
```

Zoek:

```text
X-Content-Type-Options
X-Frame-Options
Referrer-Policy
```

Controlepunt:

> Security headers zijn nuttig, maar vervangen geen login, autorisatie of patching.

---

## 13. Stap 7: bewijs dat backends niet rechtstreeks gepubliceerd zijn

Controleer:

```text
docker compose ps
```

Test:

```text
curl.exe -I http://localhost:8081
curl.exe -I http://localhost:8082
curl.exe -I http://localhost:8083
```

Vul in:

| Test | Verwacht | Werkelijk |
|---|---|---|
| `localhost:8080` met juiste hostname | werkt via Traefik | ... |
| `localhost:8081` | faalt | ... |
| `localhost:8082` | faalt | ... |
| `localhost:8083` | faalt | ... |

Controlepunt:

> Als een backend rechtstreeks via `localhost:8081` werkt, heb je de backend per ongeluk gepubliceerd.

---

## 14. Stap 8: logs en dashboard

Bekijk logs:

```text
docker compose logs reverse-proxy
```

Voer daarna opnieuw een request uit:

```text
curl.exe -I http://helpdesk.bluepeak.test:8080
```

Open:

```text
http://localhost:8088
```

Beantwoord:

- Welke routers zie je?
- Welke services zie je?
- Welke middleware zie je?
- Welke statuscode zie je in de logs?
- Waarom mag het dashboard in productie niet onbeveiligd publiek staan?

---

## 15. Stap 9: foutscenario

Maak tijdelijk een fout in `traefik/dynamic.yml`.

Wijzig bijvoorbeeld de helpdeskservice naar:

```yaml
url: "http://helpdesk:8088"
```

Test:

```text
curl.exe -I http://helpdesk.bluepeak.test:8080
docker compose logs reverse-proxy
```

Vul in:

| Fout | Symptoom | Loghint | Oplossing |
|---|---|---|---|
| verkeerde backendpoort | ... | ... | ... |

Zet daarna terug:

```yaml
url: "http://helpdesk:80"
```

Controlepunt:

> De client bereikt Traefik nog wel. De fout zit tussen Traefik en de backend.

---

## 16. Firewallvoorstel

Vertaal je lab naar productie.

Vul in:

| Bron | Bestemming | Poort | Actie | Waarom |
|---|---|---:|---|---|
| Internet | reverse proxy | 443 | allow | ... |
| Internet | intranet backend | 80 | deny | ... |
| Internet | helpdesk backend | 80 | deny | ... |
| reverse proxy | intranet backend | 80/443 | allow | ... |
| reverse proxy | helpdesk backend | 80/443 | allow | ... |
| reverse proxy | managementzone | any | deny | ... |

---

## 17. In te dienen

Lever een kort technisch verslag in met:

1. je finale `docker-compose.yml`;
2. je finale `traefik/dynamic.yml`;
3. tabel met routers, services en hostnames;
4. bewijs dat elke hostname werkt;
5. bewijs dat backendpoorten niet rechtstreeks gepubliceerd zijn;
6. security-headercontrole;
7. log- of dashboardcontrole;
8. foutscenario met analyse;
9. firewallvoorstel;
10. eindconclusie.

Neem geen secrets op.

---

## 18. Eindvraag

Sluit af met:

> Waarom is stap voor stap publiceren via Traefik veiliger en beheerbaarder dan elke webapplicatie rechtstreeks een eigen poort geven?

