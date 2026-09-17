# Workshop 8 - Interne applicaties publiceren via Traefik

## Modeloplossing voor studenten

## 1. Korte samenvatting

De student bouwde de reverse-proxyomgeving stap voor stap op.

Eerst werd alleen Traefik gestart.

Daarna kwamen de backends `intranet`, `helpdesk` en `status` erbij.

Elke backend kreeg geen hostpoort.

In `traefik/dynamic.yml` werden daarna routers, services en een middleware toegevoegd.

De applicaties zijn bereikbaar via:

```text
http://intranet.bluepeak.test:8080
http://helpdesk.bluepeak.test:8080
http://status.bluepeak.test:8080
```

De backends zijn niet bereikbaar via aparte hostpoorten.

Kernconclusie:

> Traefik publiceert de applicaties via hostnames, terwijl de backendcontainers intern blijven.

---

## 2. Stap 1: Traefik starten

De starterconfig bevat alleen `reverse-proxy`.

Belangrijke static config:

```yaml
command:
  - "--providers.file.filename=/etc/traefik/dynamic.yml"
  - "--providers.file.watch=true"
  - "--entrypoints.web.address=:80"
  - "--api.dashboard=true"
  - "--api.insecure=true"
  - "--accesslog=true"
```

Uitleg:

| Optie | Betekenis |
|---|---|
| `providers.file.filename` | Traefik leest dynamic config uit `dynamic.yml` |
| `providers.file.watch` | wijzigingen in dynamic config worden opgepikt |
| `entrypoints.web.address=:80` | Traefik luistert intern op poort 80 |
| `api.dashboard=true` | dashboard aan |
| `api.insecure=true` | dashboard lokaal zonder authenticatie voor lab |
| `accesslog=true` | requests verschijnen in de logs |

Verwachte poorten:

| Hostpoort | Containerpoort | Doel |
|---:|---:|---|
| 8080 | 80 | webverkeer naar Traefik |
| 8088 | 8080 | Traefik-dashboard |

Sterke conclusie:

> Traefik draait, maar publiceert nog geen applicaties zolang `dynamic.yml` geen routers en services bevat.

---

## 3. Stap 2: intranet-backend toevoegen

In `docker-compose.yml`:

```yaml
  intranet:
    image: nginx:alpine
    container_name: ch8-intranet
    volumes:
      - ./sites/intranet:/usr/share/nginx/html:ro
    networks:
      - appnet
```

Belangrijk:

> Er staat geen `ports:` bij de backend.

Waarom?

- de backend is alleen intern bereikbaar op het Docker-netwerk;
- Traefik kan de backend bereiken via servicenaam `intranet`;
- clients kunnen de backend niet rechtstreeks via `localhost:8081` bereiken.

Controle:

```text
docker compose ps
```

Verwacht:

- `reverse-proxy` draait;
- `intranet` draait;
- alleen Traefik publiceert hostpoorten.

---

## 4. Stap 3: intranet router en service

In `traefik/dynamic.yml`:

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

Uitleg:

| Onderdeel | Waarde | Betekenis |
|---|---|---|
| Router | `intranet` | matcht intranetverkeer |
| Rule | `Host(...)` | kijkt naar hostname |
| Entrypoint | `web` | gebruikt Traefik poort 80 |
| Service | `intranet` | naam van backenddoel in Traefik |
| URL | `http://intranet:80` | interne Docker-service op poort 80 |

Test:

```text
curl.exe -I http://intranet.bluepeak.test:8080
```

Verwacht:

```text
HTTP/1.1 200 OK
```

Sterke conclusie:

> De client bereikt Traefik via poort 8080. Traefik kiest de intranetservice op basis van de hostname.

---

## 5. Stap 4: helpdesk toevoegen

In `docker-compose.yml`:

```yaml
  helpdesk:
    image: nginx:alpine
    container_name: ch8-helpdesk
    volumes:
      - ./sites/helpdesk:/usr/share/nginx/html:ro
    networks:
      - appnet
```

In `traefik/dynamic.yml`, onder `routers:`:

```yaml
    helpdesk:
      rule: "Host(`helpdesk.bluepeak.test`)"
      entryPoints:
        - web
      service: helpdesk
```

Onder `services:`:

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

Conclusie:

> Intranet en helpdesk gebruiken dezelfde proxypoort, maar Traefik onderscheidt ze op hostname.

---

## 6. Stap 5: status toevoegen

In `docker-compose.yml`:

```yaml
  status:
    image: nginx:alpine
    container_name: ch8-status
    volumes:
      - ./sites/status:/usr/share/nginx/html:ro
    networks:
      - appnet
```

In `traefik/dynamic.yml`, onder `routers:`:

```yaml
    status:
      rule: "Host(`status.bluepeak.test`)"
      entryPoints:
        - web
      service: status
```

Onder `services:`:

```yaml
    status:
      loadBalancer:
        servers:
          - url: "http://status:80"
```

Verwachte testresultaten:

| Hostname | Verwacht |
|---|---|
| `intranet.bluepeak.test:8080` | intranetpagina |
| `helpdesk.bluepeak.test:8080` | helpdeskpagina |
| `status.bluepeak.test:8080` | statuspagina |

---

## 7. Stap 6: security headers

In `traefik/dynamic.yml`, onder `middlewares:`:

```yaml
    security-headers:
      headers:
        contentTypeNosniff: true
        frameDeny: true
        referrerPolicy: "strict-origin-when-cross-origin"
```

Elke router krijgt:

```yaml
      middlewares:
        - security-headers
```

Voorbeeld bij intranet:

```yaml
    intranet:
      rule: "Host(`intranet.bluepeak.test`)"
      entryPoints:
        - web
      service: intranet
      middlewares:
        - security-headers
```

Controle:

```text
curl.exe -I http://intranet.bluepeak.test:8080
```

Verwacht:

| Header | Waarde |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |

Conclusie:

> De reverse proxy kan headers centraal afdwingen. Dit is een extra laag, geen vervanging voor authenticatie.

---

## 8. Finale docker-compose.yml

```yaml
services:
  reverse-proxy:
    image: traefik:v3.1
    container_name: ch8-traefik
    command:
      - "--providers.file.filename=/etc/traefik/dynamic.yml"
      - "--providers.file.watch=true"
      - "--entrypoints.web.address=:80"
      - "--api.dashboard=true"
      - "--api.insecure=true"
      - "--accesslog=true"
    ports:
      - "8080:80"
      - "8088:8080"
    volumes:
      - ./traefik/dynamic.yml:/etc/traefik/dynamic.yml:ro
    depends_on:
      - intranet
      - helpdesk
      - status
    networks:
      - appnet

  intranet:
    image: nginx:alpine
    container_name: ch8-intranet
    volumes:
      - ./sites/intranet:/usr/share/nginx/html:ro
    networks:
      - appnet

  helpdesk:
    image: nginx:alpine
    container_name: ch8-helpdesk
    volumes:
      - ./sites/helpdesk:/usr/share/nginx/html:ro
    networks:
      - appnet

  status:
    image: nginx:alpine
    container_name: ch8-status
    volumes:
      - ./sites/status:/usr/share/nginx/html:ro
    networks:
      - appnet

networks:
  appnet:
    name: ch8-reverse-proxy-appnet
```

---

## 9. Finale traefik/dynamic.yml

```yaml
http:
  routers:
    intranet:
      rule: "Host(`intranet.bluepeak.test`)"
      entryPoints:
        - web
      service: intranet
      middlewares:
        - security-headers

    helpdesk:
      rule: "Host(`helpdesk.bluepeak.test`)"
      entryPoints:
        - web
      service: helpdesk
      middlewares:
        - security-headers

    status:
      rule: "Host(`status.bluepeak.test`)"
      entryPoints:
        - web
      service: status
      middlewares:
        - security-headers

  services:
    intranet:
      loadBalancer:
        servers:
          - url: "http://intranet:80"

    helpdesk:
      loadBalancer:
        servers:
          - url: "http://helpdesk:80"

    status:
      loadBalancer:
        servers:
          - url: "http://status:80"

  middlewares:
    security-headers:
      headers:
        contentTypeNosniff: true
        frameDeny: true
        referrerPolicy: "strict-origin-when-cross-origin"
```

---

## 10. Negatieve tests

```text
curl.exe -I http://localhost:8081
curl.exe -I http://localhost:8082
curl.exe -I http://localhost:8083
```

Verwacht:

| Test | Verwacht | Betekenis |
|---|---|---|
| `localhost:8081` | faalt | intranet niet rechtstreeks gepubliceerd |
| `localhost:8082` | faalt | helpdesk niet rechtstreeks gepubliceerd |
| `localhost:8083` | faalt | status niet rechtstreeks gepubliceerd |

Conclusie:

> Alleen Traefik is gepubliceerd. De backends blijven intern.

---

## 11. Foutscenario

Foute backendpoort:

```yaml
url: "http://helpdesk:8088"
```

Gevolg:

- `helpdesk.bluepeak.test` bereikt Traefik;
- Traefik kan de backend niet correct bereiken;
- andere hostnames blijven werken;
- logs wijzen richting proxy-naar-backendprobleem.

Correctie:

```yaml
url: "http://helpdesk:80"
```

Sterke conclusie:

> DNS en routering naar Traefik werken nog. De fout zit in de serviceconfiguratie naar de backend.

---

## 12. Firewallvoorstel

| Bron | Bestemming | Poort | Actie | Waarom |
|---|---|---:|---|---|
| Internet | reverse proxy | 443 | allow | publieke HTTPS-toegang |
| Internet | backends | any | deny | backends afschermen |
| reverse proxy | intranet backend | 80/443 | allow | noodzakelijke appflow |
| reverse proxy | helpdesk backend | 80/443 | allow | noodzakelijke appflow |
| reverse proxy | status backend | 80/443 | allow | noodzakelijke appflow |
| reverse proxy | managementzone | any | deny | management beschermen |

---

## 13. Eindantwoord

Stap voor stap publiceren via Traefik is veiliger en beheerbaarder dan elke webapplicatie rechtstreeks een eigen poort geven.

De backends blijven intern.

Traefik is het centrale toegangspunt.

Hostnames bepalen welke applicatie wordt gekozen.

Logging, headers, TLS en later authenticatie kunnen centraal beheerd worden.

Eindzin:

> De reverse proxy publiceert applicaties gecontroleerd, terwijl interne backendpoorten en serverdetails afgeschermd blijven.

