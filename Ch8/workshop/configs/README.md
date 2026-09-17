# Ch8 workshop configs

Deze map bevat ondersteunende bestanden voor workshop 8.

De workshop gebruikt Docker Compose met:

- Traefik als reverse proxy;
- drie interne nginx-backends;
- lokale hostnames;
- host-based routing;
- Traefik file provider;
- positieve en negatieve tests.

Studenten gebruiken de bestanden in `student/`.

Docenten gebruiken de bestanden in `teacher/`.

De studentversie is bewust een starter:

- `docker-compose.yml` bevat bij aanvang alleen Traefik;
- `traefik/dynamic.yml` bevat lege secties;
- studenten voegen backends, routers, services en middleware stap voor stap toe.

De volledige werkende eindconfiguratie staat in:

```text
teacher/reverse-proxy-lab-solution/
```

Veiligheidsregel:

> Neem geen tokens, private keys, echte productiedomeinen of interne klantgegevens op in verslagen of gedeelde bestanden.

Belangrijk leerdoel:

> Alleen de reverse proxy publiceert een hostpoort. Backends worden niet rechtstreeks gepubliceerd.

Traefik gebruikt in deze labopstelling de file provider.

De dynamic configuratie staat in:

```text
student/reverse-proxy-lab/traefik/dynamic.yml
```

Er wordt bewust geen Docker socket gemount. Dat maakt de workshop beter voorspelbaar op Docker Desktop-installaties waar sockettoegang vanuit containers door beveiligingsinstellingen geblokkeerd wordt.
