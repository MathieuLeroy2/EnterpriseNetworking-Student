# Ch8 student - lokale hostnames

In deze workshop gebruik je lokale testhostnames.

Ze moeten naar je eigen Docker-host wijzen.

Voor een lokaal lab is dat meestal:

```text
127.0.0.1
```

## Windows

Open PowerShell of Notepad als administrator.

Bestand:

```text
C:\Windows\System32\drivers\etc\hosts
```

Voeg toe:

```text
127.0.0.1 intranet.bluepeak.test
127.0.0.1 helpdesk.bluepeak.test
127.0.0.1 status.bluepeak.test
```

## Linux/macOS

Bestand:

```text
/etc/hosts
```

Voeg toe:

```text
127.0.0.1 intranet.bluepeak.test
127.0.0.1 helpdesk.bluepeak.test
127.0.0.1 status.bluepeak.test
```

## Controle

```text
ping intranet.bluepeak.test
ping helpdesk.bluepeak.test
ping status.bluepeak.test
```

Als je geen hosts file mag aanpassen, kan je testen met curl.exe en een Host header:

```text
curl.exe -H "Host: intranet.bluepeak.test" http://127.0.0.1:8080
curl.exe -H "Host: helpdesk.bluepeak.test" http://127.0.0.1:8080
curl.exe -H "Host: status.bluepeak.test" http://127.0.0.1:8080
```

