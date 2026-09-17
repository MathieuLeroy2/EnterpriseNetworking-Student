# Ch8 student - quick tests

Gebruik deze testmatrix tijdens de workshop.

## 1. Startfase

```text
docker compose up -d
docker compose ps
```

Verwacht:

- `reverse-proxy` is up;
- de applicatiecontainers zijn er nog niet zolang je ze zelf niet hebt toegevoegd;
- het Traefik-dashboard is lokaal bereikbaar via `8088`.

## 2. Eindfase

Na het toevoegen van intranet, helpdesk en status:

```text
docker compose ps
```

Verwacht:

- `intranet` is up;
- `helpdesk` is up;
- `status` is up;
- alleen de proxy publiceert `8080:80`.

## 3. Hostnames testen

```text
curl.exe -I http://intranet.bluepeak.test:8080
curl.exe -I http://helpdesk.bluepeak.test:8080
curl.exe -I http://status.bluepeak.test:8080
```

Verwacht:

- HTTP-status `200 OK`;
- elke hostname toont de juiste applicatie.

## 4. Alternatief zonder hosts file

```text
curl.exe -I -H "Host: intranet.bluepeak.test" http://127.0.0.1:8080
curl.exe -I -H "Host: helpdesk.bluepeak.test" http://127.0.0.1:8080
curl.exe -I -H "Host: status.bluepeak.test" http://127.0.0.1:8080
```

## 5. Backends niet rechtstreeks

```text
curl.exe -I http://localhost:8081
curl.exe -I http://localhost:8082
curl.exe -I http://localhost:8083
```

Verwacht:

- deze testen falen;
- er zijn geen aparte hostpoorten voor backends.

## 6. Logs

```text
docker compose logs reverse-proxy
```

Zoek:

- statuscodes;
- hostnames;
- foutmeldingen bij verkeerde backendconfiguratie.

## 7. Traefik-dashboard

Open:

```text
http://localhost:8088
```

Controleer:

- routers voor intranet, helpdesk en status;
- services voor intranet, helpdesk en status;
- middleware `security-headers`.

## 8. Security headers

```text
curl.exe -I http://intranet.bluepeak.test:8080
```

Zoek:

```text
X-Content-Type-Options
X-Frame-Options
Referrer-Policy
```

## 9. Lab stoppen

```text
docker compose down
```
