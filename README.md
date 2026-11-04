# SAE M2 — Emplois du temps, Groupe 3 (agentique)

Module de gestion des emplois du temps d'un SIS/ERP éducatif (sous-projet B de la SAE M2 DFS & DE, 2026-2027).

Nous sommes le groupe **agentique** : le code est produit autant que possible par des agents IA, sous contrôle humain, et chaque usage de l'IA est mesuré (voir [`journal/`](journal/README.md)). Le groupe 2 développe le même module en approche classique ; la comparaison des deux approches fait partie du rendu.

Ce dépôt est notre fork du starter commun aux 4 groupes (même schéma de base, même socle d'API).

## Équipe

| Nom | Parcours | Rôle |
| :--- | :--- | :--- |
| Daniel GUERRA | DE | Référent Data : BDD, import CSV, génération des emplois du temps |
| Thomas SANNA | DE | BDD, import CSV, génération des emplois du temps |
| Clément LORIEAU | DFS | Référent API : auth, API, front |
| Simon COSSAIS | DFS | Auth, API, front |
| Thibaut RENAUD | DFS | Auth, API, front |

## Lancer

```bash
docker compose up --build
```

- API : http://localhost:8000, documentation interactive : http://localhost:8000/docs
- Postgres : `localhost:5432`, utilisateur / mot de passe / base : `sae` / `sae` / `sae`
- Adminer (facultatif) : `docker compose --profile tools up`, puis http://localhost:8080

Si un port est déjà pris, copiez `.env.example` en `.env` et changez `POSTGRES_PORT` ou `API_PORT`.

### Base de données

`db/init.sql` n'est exécuté **qu'au premier démarrage**. Après une modification, recréez la base :

```bash
docker compose down -v   # supprime les données
docker compose up
```

Données déjà présentes :
- rôles : `ADMIN`, `MANAGER`, `TEACHER`, `STUDENT`
- types de séance : `CM`, `TD`, `TP`, `EXAM` (avec leurs couleurs)
- un compte admin : `admin@example.com` / `admin1234` (mot de passe hashé en bcrypt)

### Backend

Le code est rechargé automatiquement à chaque sauvegarde. Pour ajouter une dépendance Python : l'ajouter dans `backend/requirements.txt`, puis `docker compose up --build`.

## Organisation du dépôt

```
AGENTS.md          consignes pour les agents IA (et conventions de code)
backend/           API FastAPI
db/init.sql        schéma complet + données de référence (source de vérité)
docs/              cadrage, spécification, métriques, changelog du schéma et de l'API
journal/           journal d'usage de l'IA et scripts de métriques
rapport/           documents pour l'enseignant (Typst)
```

## Travailler sur le projet

- **Branches** : `feature/<nom>`, `fix/<nom>` ou `docs/<nom>`, puis PR vers `dev`. `main` ne reçoit que des PR depuis `dev`.
- **Commits** : Conventional Commits en anglais, avec le trailer d'origine du code (`IA: genere`, `IA: retouche`, rien pour du code écrit à la main). Activez le modèle : `git config commit.template .gitmessage`.
- **Schéma et API** : toute modification passe par une ligne dans [`docs/CHANGELOG-schema-api.md`](docs/CHANGELOG-schema-api.md).
- **Journal** : une ligne par tâche dans `journal/ia.csv`, mode d'emploi dans [`journal/README.md`](journal/README.md).
- **Agents IA** : ils lisent [`AGENTS.md`](AGENTS.md), qui contient les règles du projet (commandes, conventions de code, sécurité, limites).
