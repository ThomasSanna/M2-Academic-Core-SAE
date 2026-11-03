# SAE — base commune (back + données)

Base à forker : une base PostgreSQL et une API FastAPI, lancées avec Docker.
Le front est propre à chacun (voir la fin de `docker-compose.yml`).

```
bdd/init.sql        schéma complet + données de référence
backend/main.py     l'API (une seule route d'exemple, à compléter)
docs/infos.md       spécification (routes, modèle de données)
```

## Lancer

```bash
docker compose up --build
```

- API : http://localhost:8000 — doc interactive : http://localhost:8000/docs
- Postgres : `localhost:5432`, utilisateur / mot de passe / base : `sae` / `sae` / `sae`
- Adminer (facultatif) : `docker compose --profile tools up`, puis http://localhost:8080

Si un port est déjà pris, copiez `.env.example` en `.env` et changez `POSTGRES_PORT` ou `API_PORT`.

## Base de données

`bdd/init.sql` n'est exécuté **qu'au premier démarrage**. Après l'avoir modifié, recréez la base :

```bash
docker compose down -v   # supprime les données
docker compose up
```

Données déjà présentes :
- rôles : `ADMIN`, `MANAGER`, `TEACHER`, `STUDENT`
- types de séance : `CM`, `TD`, `TP`, `EXAM` (avec leurs couleurs)
- un compte admin : `admin@example.com` / `admin1234` (mot de passe hashé en bcrypt)

## Backend

`backend/main.py` contient une petite fonction `query(sql, params)` et une route d'exemple (`GET /roles`).
Ajoutez vos routes dans ce fichier (ou découpez-le comme vous voulez). Le code est rechargé automatiquement à chaque sauvegarde.

Pour ajouter une dépendance Python : l'ajouter dans `backend/requirements.txt`, puis `docker compose up --build`.
