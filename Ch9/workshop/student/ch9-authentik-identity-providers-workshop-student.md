# Workshop 9 - Centrale identiteit en SSO met Authentik

## 1. Situering

In hoofdstuk 8 publiceerde je webapplicaties via een centraal toegangspunt.

In deze workshop voeg je een andere enterprisebouwsteen toe: **centrale identiteit**.

Je bouwt stap voor stap:

1. een lokale Authentik-omgeving;
2. een gebruikers- en groepenstructuur;
3. een application en OAuth2/OIDC-provider;
4. een koppeling met een lokale OIDC-client;
5. groepsgebaseerde toegang;
6. single sign-on;
7. TOTP als tweede factor;
8. lifecycle- en audittests.

Je krijgt niet alleen een werkende login. Je moet aantonen:

- wie authenticatie uitvoert;
- welke identity-informatie de applicatie ontvangt;
- welke groep toegang krijgt;
- dat een niet-toegelaten gebruiker geweigerd wordt;
- wat er gebeurt bij MFA, deactivatie en sessies;
- welke gebeurtenissen in de auditlogs verschijnen.

Veiligheidsregel:

> Neem geen wachtwoorden, secrets, tokens, TOTP-QR-codes of herstelcodes op in je
> verslag.

---

## 2. Scenario

**BluePeak Services** gebruikt steeds meer interne webapplicaties.

Vandaag heeft elke applicatie eigen accounts. Daardoor ontstaan problemen:

- IT moet accounts op meerdere plaatsen maken en verwijderen;
- medewerkers hergebruiken wachtwoorden;
- externe partners krijgen soms te brede toegang;
- er is geen centraal overzicht van logins;
- gevoelige toegang gebruikt nog geen MFA.

BluePeak wil Authentik als centrale identity provider testen.

Voor deze proof of concept gelden de volgende requirements:

| Requirement | Uitwerking in het lab |
|---|---|
| centrale identiteit | gebruikers worden in Authentik beheerd |
| SSO | de lokale applicatie delegeert login aan Authentik |
| medewerkersapp | alleen `bp-employees` krijgt toegang |
| IT-medewerker | is lid van `bp-employees` en `bp-it` |
| externe partner | is alleen lid van `bp-partners` |
| MFA-test | IT-gebruiker registreert TOTP en test een nieuwe login |
| lifecycle | account wordt tijdelijk gedeactiveerd |
| auditing | login, deny en beheerwijziging worden onderzocht |

Centrale onderzoeksvraag:

> Hoe centraliseer je login en applicatietoegang zonder te veronderstellen dat elk
> bestaand account automatisch elke applicatie mag gebruiken?

---

## 3. Beginsituatie

Werk in:

```text
Ch9/workshop/configs/student/authentik-lab
```

Je krijgt:

| Bestand | Doel |
|---|---|
| `compose.yml` | Authentik, PostgreSQL en lokale OIDC-client |
| `.env.example` | voorbeeld van lokale omgevingsvariabelen |
| `.gitignore` | voorkomt dat lokale secrets en data worden toegevoegd |
| `oidc-client/app.py` | didactische lokale OIDC-client |

De OIDC-client bewaart geen lokale gebruikerswachtwoorden.

De client is bij de start nog niet gekoppeld. Je maakt eerst zelf een provider in
Authentik en vult daarna de gegenereerde clientgegevens lokaal in.

---

## 4. Doelen

Na deze workshop kan je:

1. een Authentik-labomgeving gecontroleerd starten;
2. de functies van database, server, worker en OIDC-client onderscheiden;
3. gebruikers en groepen volgens een accessmodel maken;
4. een Authentik application en provider onderscheiden;
5. een confidential OIDC-client met strikte redirect URI registreren;
6. een application binding aan een groep koppelen;
7. een authorization code flow observeren;
8. UserInfo-claims interpreteren;
9. SSO aantonen zonder alleen op browsergedrag te gokken;
10. TOTP registreren en een MFA-prompt testen;
11. een toegelaten en een geweigerde gebruiker testen;
12. de impact van accountdeactivatie en sessies onderzoeken;
13. relevante audit events terugvinden;
14. een identity-, access- en MFA-policy documenteren.

---

## 5. Benodigdheden

Je hebt nodig:

- Docker Desktop of Docker Engine;
- Docker Compose v2;
- minstens 2 CPU-cores en 2 GB vrij RAM voor de labstack;
- browser met private/incognitovenster;
- terminal;
- een TOTP-compatibele authenticator voor de MFA-test;
- de cursus van hoofdstuk 9.

De eerste start downloadt containerimages en kan enkele minuten duren.

Poorten in dit lab:

| URL | Doel |
|---|---|
| `http://localhost:9000` | Authentik |
| `https://localhost:9443` | lokale Authentik HTTPS-poort met labcertificaat |
| `http://localhost:8089` | BluePeak OIDC-labclient |

Gebruik voor de workshop de opgegeven HTTP-URL's. In productie is HTTPS verplicht.

---

## 6. Identiteiten en verwachte toegang

Maak tijdens het lab deze logische testidentiteiten.

Je mag de namen aanpassen wanneer de docent dat vraagt.

| Gebruiker | Type | Groepen | Verwachte toegang portal |
|---|---|---|---|
| Alice Vermeulen | medewerker | `bp-employees` | allow |
| Bob Peeters | IT-medewerker | `bp-employees`, `bp-it` | allow |
| Eva Partner | externe partner | `bp-partners` | deny |

Gebruik unieke labwachtwoorden die je niet elders gebruikt.

Neem de wachtwoorden niet op in je verslag.

---

## 7. Stap 1: bereid de omgeving voor

Maak een lokale `.env` op basis van het voorbeeld.

PowerShell:

```powershell
Copy-Item .env.example .env
```

Open `.env` en vervang:

```text
PG_PASS=CHANGE_ME_RANDOM_DATABASE_PASSWORD
AUTHENTIK_SECRET_KEY=CHANGE_ME_RANDOM_AUTHENTIK_SECRET
```

door twee verschillende, willekeurige waarden.

Laat voorlopig staan:

```text
OIDC_CLIENT_ID=CHANGE_ME_AFTER_PROVIDER_CREATION
OIDC_CLIENT_SECRET=CHANGE_ME_AFTER_PROVIDER_CREATION
```

Controleer:

```powershell
docker compose config --services
```

Verwacht:

```text
postgresql
server
worker
oidc-client
```

Beantwoord:

- Waarom zijn `PG_PASS` en `AUTHENTIK_SECRET_KEY` verschillend?
- Waarom staat `.env` in `.gitignore`?
- Waarom staat de Docker socket niet in `compose.yml` gemount?

Controlepunt:

> Je kan de Compose-config valideren zonder de waarden van secrets in je verslag te
> tonen.

---

## 8. Stap 2: start Authentik

Start:

```powershell
docker compose up -d
```

Controleer:

```powershell
docker compose ps
docker compose logs server --tail 30
docker compose logs worker --tail 30
```

Wacht tot de server klaar is en open:

```text
http://localhost:9000
```

Doorloop de initiële setup voor `akadmin`.

Kies zelf een sterk lokaal labwachtwoord. Deel of documenteer het niet.

Vul in:

| Component | Functie | Status |
|---|---|---|
| `postgresql` | ... | ... |
| `server` | ... | ... |
| `worker` | ... | ... |
| `oidc-client` | ... | ... |

Open ook:

```text
http://localhost:8089
```

Verwacht:

> De OIDC-client meldt dat client ID en client secret nog geconfigureerd moeten
> worden.

Dit is op dit moment geen fout.

---

## 9. Stap 3: maak de groepen

Open de Authentik Admin interface.

Ga naar:

```text
Directory > Groups
```

Maak:

```text
bp-employees
bp-it
bp-partners
```

Gebruik eenvoudige, herkenbare namen.

Maak groepen niet superuser en ken geen Authentik-beheersrollen toe.

Beantwoord:

- Waarom krijgt `bp-it` niet automatisch superuserrechten?
- Wat is het verschil tussen een doelgroepgroep en een Authentik-beheersrol?
- Waarom maken we een aparte partnergroep?

Controlepunt:

> De drie groepen bestaan, maar geven nog geen applicatietoegang. Er is nog geen
> application binding.

---

## 10. Stap 4: maak de testgebruikers

Ga naar:

```text
Directory > Users
```

Maak drie interne gebruikers.

Gebruik bijvoorbeeld:

| Username | Naam | E-mail |
|---|---|---|
| `alice.vermeulen` | Alice Vermeulen | `alice.vermeulen@bluepeak.test` |
| `bob.peeters` | Bob Peeters | `bob.peeters@bluepeak.test` |
| `eva.partner` | Eva Partner | `eva@partner.test` |

Stel voor elke gebruiker een uniek lokaal labwachtwoord in.

Koppel de groepen:

| Gebruiker | Groepen |
|---|---|
| Alice | `bp-employees` |
| Bob | `bp-employees`, `bp-it` |
| Eva | `bp-partners` |

Controleer per gebruiker de detailpagina.

Lever geen screenshot in waarop een wachtwoord of recoverylink staat.

Beantwoord:

- Waarom is Bob lid van twee groepen?
- Waarom is Eva niet ook lid van `bp-employees`?
- Welke lifecycle-informatie ontbreekt nog voor een echt partneraccount?

---

## 11. Stap 5: test centrale login vóór de applicatiekoppeling

Open een private browser.

Ga naar:

```text
http://localhost:9000
```

Meld aan als Alice.

Observeer:

- welke interface Alice ziet;
- of Alice de Admin interface kan openen;
- welke applicaties zichtbaar zijn;
- welke gebruikersinstellingen beschikbaar zijn.

Meld Alice daarna volledig af bij Authentik.

Herhaal één keer met Eva.

Vul in:

| Test | Verwacht | Werkelijk |
|---|---|---|
| Alice kan centraal aanmelden | ja | ... |
| Alice is Authentik-admin | nee | ... |
| BluePeak Portal zichtbaar | nog niet | ... |
| Eva kan centraal aanmelden | ja | ... |
| Eva heeft automatisch medewerkersapp-toegang | nog niet bepaald | ... |

Kernvraag:

> Waarom bewijst een geslaagde login bij Authentik nog niet dat Eva toegang tot het
> medewerkersportaal heeft?

---

## 12. Stap 6: maak application en OIDC-provider

Meld opnieuw aan als `akadmin`.

Ga naar:

```text
Applications > Applications
```

Maak een nieuwe application met provider.

Afhankelijk van de exacte UI-versie heet de actie bijvoorbeeld `New Provider` of
`Create with Provider`.

### Application

Gebruik:

| Instelling | Waarde |
|---|---|
| Name | `BluePeak Portal` |
| Slug | `bluepeak-portal` |
| Launch URL | `http://localhost:8089/` |

### Provider

Kies:

```text
OAuth2/OIDC
```

Gebruik:

| Instelling | Waarde |
|---|---|
| Client type | `Confidential` |
| Redirect URI matching | `Strict` |
| Redirect URI | `http://localhost:8089/callback` |
| Signing key | beschikbare Authentik signing key |
| Scopes/property mappings | `openid`, `profile`, `email` |
| Authorization flow | standaard expliciete of impliciete consentflow volgens docent |
| Authentication flow | standaard authentication flow |
| Invalidation flow | standaard provider invalidation flow |

Gebruik geen wildcard redirect URI.

Noteer lokaal, buiten je verslag:

- client ID;
- client secret.

Beantwoord:

- Welke instellingen horen bij de application?
- Welke instellingen horen bij de provider?
- Waarom is de client ID niet hetzelfde als het client secret?
- Waarom gebruiken we een strikte redirect URI?
- Waarom vragen we geen `offline_access`?

Controlepunt:

> Authentik kent nu de applicatie en het protocol, maar de lokale OIDC-client kent zijn
> clientgegevens nog niet.

---

## 13. Stap 7: koppel de lokale OIDC-client

Open lokaal `.env`.

Vervang:

```text
OIDC_CLIENT_ID=CHANGE_ME_AFTER_PROVIDER_CREATION
OIDC_CLIENT_SECRET=CHANGE_ME_AFTER_PROVIDER_CREATION
```

door de waarden van de zojuist gemaakte provider.

Toon deze regels niet in screenshots of je verslag.

Pas de omgeving toe:

```powershell
docker compose up -d
docker compose logs oidc-client --tail 20
```

Open:

```text
http://localhost:8089
```

Verwacht:

> De knop `Aanmelden via Authentik` is zichtbaar.

Maak een configuratietabel zonder secretwaarden:

| Onderdeel | Waarde |
|---|---|
| application slug | `bluepeak-portal` |
| client type | confidential |
| redirect URI | `http://localhost:8089/callback` |
| scopes | `openid profile email` |
| authorization endpoint | pad eindigt op `/application/o/authorize/` |
| token endpoint | pad eindigt op `/application/o/token/` |
| UserInfo endpoint | pad eindigt op `/application/o/userinfo/` |

---

## 14. Stap 8: bind toegang aan de medewerkersgroep

Open in Authentik:

```text
Applications > Applications > BluePeak Portal
```

Open:

```text
Policy / Group / User Bindings
```

Maak of bind:

```text
Group: bp-employees
```

Controleer dat je niet per ongeluk `bp-partners` bindt.

Beantwoord:

- Wat gebeurt er wanneer een application geen bindings heeft?
- Op welk object staat de binding: application of provider?
- Waarom gebruiken we een groep en geen drie individuele user bindings?

Maak vooraf je testverwachting:

| Gebruiker | Relevante groep | Verwacht |
|---|---|---|
| Alice | `bp-employees` | ... |
| Bob | `bp-employees`, `bp-it` | ... |
| Eva | `bp-partners` | ... |

---

## 15. Stap 9: test Alice en onderzoek de OIDC-flow

Gebruik een nieuw private browservenster.

1. Open `http://localhost:8089`.
2. Klik `Aanmelden via Authentik`.
3. Meld aan als Alice.
4. Geef consent als de gekozen flow dit vraagt.
5. Observeer de terugkeer naar de lokale client.

Let tijdens de flow op de URL in de browser.

Zoek conceptueel:

- `client_id`;
- `redirect_uri`;
- `response_type=code`;
- `scope`;
- `state`;
- het authorization endpoint;
- de callback.

Neem geen screenshot van de callbackquery of tokens.

Vul in:

| Observatie | Antwoord |
|---|---|
| Wie vroeg het wachtwoord? | ... |
| Kreeg de OIDC-client het wachtwoord? | ... |
| Welke redirect URI werd gebruikt? | ... |
| Welke UserInfo-claims zijn zichtbaar? | ... |
| Welke groepenclaim is zichtbaar? | ... |
| Welke lokale app-sessie ontstond? | ... |

Controlepunt:

> Alice is centraal geauthenticeerd, door de application binding geautoriseerd en door
> de OIDC-client als aangemelde gebruiker herkend.

---

## 16. Stap 10: bewijs single sign-on

Terwijl Alice nog bij Authentik aangemeld is:

1. klik in de OIDC-client op `Alleen lokaal uitloggen`;
2. controleer dat de lokale client opnieuw de aanmeldknop toont;
3. klik opnieuw op `Aanmelden via Authentik`;
4. observeer of Alice haar wachtwoord opnieuw moet invoeren.

Beantwoord:

- Welke sessie werd beëindigd door `Alleen lokaal uitloggen`?
- Welke sessie bleef bestaan?
- Waarom kan de tweede login zonder nieuwe wachtwoordprompt verlopen?
- Is lokaal uitloggen hetzelfde als single logout?

Bewijs SSO met een korte beschrijving van de twee sessies. Een screenshot alleen is
niet voldoende.

---

## 17. Stap 11: voer de negatieve partnertest uit

Beëindig eerst de Authentik-sessie van Alice.

Gebruik bij twijfel een volledig nieuw private browservenster.

1. Open `http://localhost:8089`.
2. Klik `Aanmelden via Authentik`.
3. Meld aan als Eva.
4. Observeer waar de toegang wordt geweigerd.
5. Controleer of de OIDC-client een lokale aangemelde sessie maakt.

Vul in:

| Vraag | Antwoord |
|---|---|
| Waren Eva's credentials geldig? | ... |
| Is Eva geauthenticeerd? | ... |
| Is Eva geautoriseerd voor BluePeak Portal? | ... |
| Welke policy/binding veroorzaakte dit resultaat? | ... |
| Ontstond een lokale applicatiesessie? | ... |

Controlepunt:

> Een geldige identiteit kan correct aangemeld zijn en toch geen toegang tot een
> specifieke applicatie krijgen.

---

## 18. Stap 12: registreer en test TOTP voor Bob

Meld als Bob aan bij Authentik.

Open de gebruikersinstellingen via het profielmenu.

Zoek de MFA- of authenticatorinstellingen en registreer een TOTP-device.

Belangrijk:

- scan de QR-code alleen met je eigen labauthenticator;
- neem geen screenshot van de QR-code of seed;
- deel geen herstelcodes;
- verwijder het labdevice na de workshop als de docent dat vraagt.

Meld Bob volledig af bij:

- de OIDC-client;
- Authentik.

Open een nieuw private browservenster en meld Bob via de OIDC-client opnieuw aan.

Observeer:

- wachtwoordstap;
- TOTP-stap;
- uiteindelijke toegang;
- relevante events.

Vul in:

| Test | Verwacht | Werkelijk |
|---|---|---|
| correct wachtwoord, geen TOTP | login niet voltooid | ... |
| correct wachtwoord, foute TOTP | login faalt | ... |
| correct wachtwoord, correcte TOTP | login slaagt | ... |
| Bob krijgt portaltoegang | ja, via `bp-employees` | ... |

Beantwoord:

- Welke twee factorcategorieën gebruikte Bob?
- Waarom geeft lidmaatschap van `bp-it` op zichzelf geen MFA?
- Is MFA in deze labflow verplicht voor een gebruiker zonder geregistreerd device?
- Wat moet een productiepolicy extra afdwingen?

Controlepunt:

> Je hebt niet alleen TOTP geregistreerd; je hebt met een nieuwe login gecontroleerd
> of de factor in de authentication flow gevalideerd wordt.

---

## 19. Stap 13: onderzoek claims en dataminimalisatie

Bekijk de UserInfo-claims die de OIDC-client voor Alice of Bob toont.

Classificeer:

| Claim | Nodig voor deze app? | Mogelijk gebruik | Risico bij onnodig delen |
|---|---|---|---|
| `sub` | ... | ... | ... |
| `preferred_username` | ... | ... | ... |
| `email` | ... | ... | ... |
| `groups` | ... | ... | ... |
| andere claim | ... | ... | ... |

Beantwoord:

- Welke claim is geschikt als stabiele technische identifier?
- Waarom is een e-mailadres niet altijd een goede primaire sleutel?
- Welke claims zou een publieke statuspagina niet nodig hebben?
- Waarom toont de labclient geen volledige tokens?

---

## 20. Stap 14: lifecycle-test met deactivatie

Meld Alice aan bij de OIDC-client en laat de lokale sessie open.

Meld in een andere browser aan als `akadmin`.

Deactiveer Alice tijdelijk.

Test afzonderlijk:

1. vernieuw Alice's al geopende OIDC-clientpagina;
2. log Alice alleen lokaal uit;
3. probeer opnieuw via Authentik aan te melden;
4. controleer en beëindig waar mogelijk Alice's actieve Authentik-sessie;
5. probeer opnieuw.

Vul in:

| Test | Resultaat | Verklaring |
|---|---|---|
| bestaande lokale app-sessie vernieuwen | ... | ... |
| nieuwe authenticatie als gedeactiveerde Alice | ... | ... |
| na intrekken centrale sessie | ... | ... |

Activeer Alice opnieuw na de test.

Kernvraag:

> Waarom is een account deactiveren niet altijd voldoende om elke reeds bestaande
> applicatiesessie onmiddellijk te beëindigen?

---

## 21. Stap 15: onderzoek audit events

Open als beheerder:

```text
Events > Logs
```

Zoek gebeurtenissen voor:

- een geslaagde login;
- een mislukte login of foute TOTP;
- Eva's geweigerde applicatietoegang;
- de wijziging van Alice's actieve status;
- een groeps- of gebruikerswijziging;
- een OIDC authorization.

Noteer geen tokens, secrets of volledige gevoelige eventpayloads.

Maak een audittabel:

| Event | Tijd | Actor/target | Resultaat | Waarom relevant |
|---|---|---|---|---|
| geslaagde login | ... | ... | ... | ... |
| geweigerde toegang | ... | ... | ... | ... |
| user update | ... | ... | ... | ... |
| MFA-event | ... | ... | ... | ... |

Beantwoord:

- Welke events helpen bij een accountcompromis?
- Welke beheerwijziging ging aan de lifecycle-test vooraf?
- Welke informatie wil je naar een centraal SIEM sturen?
- Waarom mogen credentials niet in auditlogs staan?

---

## 22. Stap 16: maak een identity- en accessmodel

Vertaal het lab naar een voorstel voor BluePeak.

### Gebruikers en groepen

| Identiteitstype | Groep | Eigenaar | Reviewfrequentie | Offboarding |
|---|---|---|---|---|
| medewerker | ... | ... | ... | ... |
| IT | ... | ... | ... | ... |
| partner | ... | ... | ... | ... |

### Applicatiematrix

| Applicatie | Toegangsgroep | MFA | Belangrijke claims | Sessierisico |
|---|---|---|---|---|
| intranet | ... | ... | ... | ... |
| helpdesk | ... | ... | ... | ... |
| monitoring | ... | ... | ... | ... |
| adminportaal | ... | ... | ... | ... |
| partnerportaal | ... | ... | ... | ... |

### MFA-policy

Beschrijf:

- voor wie MFA verplicht is;
- bij welke applicaties;
- welke factoren toegelaten zijn;
- hoe enrollment gebeurt;
- wat bij verlies van een factor gebeurt;
- wie recovery mag uitvoeren;
- welke events gemonitord worden.

---

## 23. Foutscenario's

Voer minstens één toegewezen foutscenario uit.

### Scenario A: foute redirect URI

Wijzig de redirect URI in de provider tijdelijk naar een andere poort.

Test de login.

Analyseer:

- bereikt de browser Authentik?
- worden credentials aanvaard?
- waar wordt de flow gestopt?
- welke foutmelding of loghint verschijnt?

Zet daarna de strikte URI terug op:

```text
http://localhost:8089/callback
```

### Scenario B: fout client secret

Vervang lokaal tijdelijk het OIDC client secret door een foutwaarde.

Pas toe:

```powershell
docker compose up -d
```

Analyseer:

- lukt de authorizationstap?
- bereikt de browser de callback?
- welke server-to-serverstap faalt?
- waarom mag het echte secret niet in je bewijs staan?

Herstel daarna het secret.

### Scenario C: ontbrekende group binding

Verwijder tijdelijk de `bp-employees` binding.

Test Alice en Eva opnieuw.

Analyseer:

- is de toepassing zonder bindings breder of smaller toegankelijk?
- waarom moet je default gedrag expliciet testen?

Herstel daarna de binding.

Gebruik deze analysetabel:

| Fout | Waar in de flow? | Symptoom | Loghint | Herstel |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

---

## 24. Typische fouten en hints

| Symptoom | Mogelijke richting | Hint |
|---|---|---|
| Authentik opent niet | containers starten nog | controleer `docker compose ps` en serverlogs |
| OIDC-client vraagt configuratie | placeholders nog actief | vul client ID en secret lokaal in |
| callback geeft tokenfout | secret of redirect URI fout | vergelijk beide kanten zonder secret te tonen |
| Eva krijgt toegang | binding ontbreekt of verkeerde groep | controleer application bindings |
| Bob krijgt geen TOTP-prompt | IdP-sessie bestaat of device niet bevestigd | volledig afmelden en nieuw private venster |
| andere gebruiker blijft aangemeld | centrale SSO-sessie bestaat | beëindig Authentik-sessie |
| claims ontbreken | scopes/property mappings | controleer providerconfig |
| gebruikers kunnen Admin openen | te brede beheersrechten | controleer superuser en rollen |
| deactivatie lijkt niets te doen | lokale sessie bestaat nog | onderscheid app- en IdP-sessie |
| poort 9000 bezet | andere lokale service | meld dit aan docent; wijzig niet willekeurig alle URL's |

Werk methodisch:

1. bepaal in welke fase de fout zit;
2. controleer browsergedrag;
3. controleer Authentik events;
4. controleer de OIDC-clientlogs;
5. wijzig één instelling;
6. test opnieuw.

---

## 25. Opruimen

Stop de containers zonder data te wissen:

```powershell
docker compose down
```

Wis volumes alleen wanneer de docent dit expliciet vraagt:

```powershell
docker compose down -v
```

Let op:

> `-v` verwijdert de labdatabase. Alle gebruikers, groepen, providerinstellingen en
> events gaan dan verloren.

Verwijder na afloop indien gevraagd ook het TOTP-labdevice uit je authenticator.

---

## 26. In te dienen

Lever een kort technisch verslag in met:

1. componentenoverzicht van de Compose-stack;
2. gebruikers- en groepenmatrix;
3. application- en providerconfiguratie zonder secrets;
4. schets van de authorization code flow;
5. positieve test voor Alice;
6. positieve test en MFA-observatie voor Bob;
7. negatieve toegangstest voor Eva;
8. SSO-analyse met IdP- en applicatiesessie;
9. claimanalyse;
10. lifecycle-test;
11. audittabel;
12. identity-, access- en MFA-policy;
13. foutscenario met oorzaak en herstel;
14. eindconclusie.

Niet indienen:

- `.env`;
- wachtwoorden;
- client secret;
- volledige tokens;
- TOTP-seed, QR-code of herstelcodes;
- volledige database of datavolume.

---

## 27. Eindvraag

Sluit af met:

> Hoe zorgen centrale authenticatie, groepsgebaseerde autorisatie, MFA, lifecyclebeheer
> en auditlogs samen voor betere enterprise security, en welk nieuw risico ontstaat
> doordat veel applicaties van dezelfde identity provider afhankelijk worden?
