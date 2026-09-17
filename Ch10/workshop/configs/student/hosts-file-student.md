# Ch10 - Lokale hostnames

Voeg voor het lab tijdelijk toe aan je hosts file (C:\Windows\System32\drivers\etc) !Maak eerst een lokale kopie van de huidige hostfile alvorens je deze wijzigt!:

```text
127.0.0.1 auth.bluepeak.test
127.0.0.1 public.bluepeak.test
127.0.0.1 intranet.bluepeak.test
127.0.0.1 monitoring.bluepeak.test
127.0.0.1 admin.bluepeak.test
127.0.0.1 partner.bluepeak.test
```

Alle hostnames wijzen bewust naar Traefik.

Geen hostname mag rechtstreeks naar een backendcontainer wijzen.

Verwijder de tijdelijke regels na de workshop wanneer je docent dit vraagt.

