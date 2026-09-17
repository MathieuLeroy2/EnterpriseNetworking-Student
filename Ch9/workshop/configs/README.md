# Ch9 workshop configs

Deze map bevat de ondersteunende bestanden voor workshop 9.

De workshop gebruikt Docker Compose met:

- PostgreSQL als Authentik-database;
- Authentik server en worker;
- een lokale didactische OIDC-client;
- gebruikers, groepen en application bindings die studenten in de webinterface maken;
- positieve en negatieve login- en toegangstesten.

Studenten werken in:

```text
Ch9/workshop/configs/student/authentik-lab
```

Docenten vinden verwachte instellingen en testresultaten in:

```text
Ch9/workshop/configs/teacher
```

## Versie

De Compose-stack is vastgezet op Authentik `2026.5.3`.

De officiële Authentik Compose-configuratie was het uitgangspunt. Voor dit lab is de
Docker socket bewust niet gemount: automatische outpostdeployment is niet nodig in
hoofdstuk 9 en een Docker socket mount geeft een container verregaande controle over
de Docker-host.

Controleer voor een nieuw academiejaar:

- de actuele ondersteunde Authentik-versie;
- gewijzigde menunamen in de webinterface;
- release notes voor breaking changes;
- de officiële installatievereisten.

Officiële referenties, gecontroleerd op 8 juli 2026:

- [Docker Compose installation](https://docs.goauthentik.io/install-config/install/docker-compose/)
- [Create an OAuth2 provider](https://docs.goauthentik.io/add-secure-apps/providers/oauth2/create-oauth2-provider/)
- [Working with policies](https://docs.goauthentik.io/customize/policies/working_with_policies)
- [Authenticator validation stage](https://docs.goauthentik.io/add-secure-apps/flows-stages/stages/authenticator_validate/)
- [Events](https://docs.goauthentik.io/sys-mgmt/events/)

## Secrets

Het bestand `.env.example` bevat alleen placeholders.

Studenten maken lokaal een `.env` en nemen dat bestand niet op in hun indiening.

Nooit delen:

- `AUTHENTIK_SECRET_KEY`;
- `PG_PASS`;
- OIDC client secret;
- volledige ID-, access- of refresh tokens;
- TOTP-seed of QR-code;
- herstelcodes.

## Labclient

De OIDC-client in `oidc-client/app.py` gebruikt alleen de Python standard library.
Hij maakt de authorization code flow zichtbaar en vraagt UserInfo op.

De client:

- controleert `state`;
- gebruikt een server-side labsessie;
- toont geen ruwe tokens;
- toont identity-claims uit UserInfo;
- gebruikt HTTP op localhost.

De client is geen productievoorbeeld. Volledige JWT-validatie, HTTPS, veilige
secretopslag, persistent sessiebeheer en productiehardening vallen buiten dit lab.
