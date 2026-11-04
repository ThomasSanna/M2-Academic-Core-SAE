# AGENTS.md — SAE M2, Groupe 3 (emplois du temps, approche agentique)

Fork du starter commun aux 4 groupes : SIS/ERP éducatif, sous-projet B (emplois du temps). Nous sommes le groupe **agentique** : le plus de code possible produit par des agents, et chaque usage de l'IA est mesuré. Le groupe 2 travaille sur les mêmes objectifs en approche classique. L'intégration avec lui viendra plus tard, et chaque groupe a sa propre base.

## Commandes

```bash
docker compose up --build                 # API :8000 (/docs), Postgres :5432 (sae/sae/sae)
docker compose --profile tools up         # + Adminer :8080
docker compose down -v && docker compose up   # rejoue db/init.sql : SUPPRIME les données
typst compile rapport/<fichier>.typ       # documents pour l'enseignant
python journal/tokens.py --since "AAAA-MM-JJ HH:MM"   # tours/tokens/coût d'une tâche
python journal/stats.py                   # agrégation du journal et des trailers
```

- Pour ajouter une dépendance Python : l'ajouter dans `backend/requirements.txt`, puis `docker compose up --build`.
- Pas encore de tests ni de CI. Cible : pytest + GitHub Actions (couverture, mutmut, radon).

## Stack

FastAPI + PostgreSQL 16 via psycopg, sans ORM : helper `query(sql, params)` dans `backend/main.py`. JWT + RBAC (pas encore implémenté). Docker compose. Front : React/Next.js + Tailwind + shadcn/ui (pas encore créé, géré par les DFS). Déploiement prévu, pas encore en place : sur push `main`, GitHub Actions construit les images, les pousse sur ghcr et les déploie sur un VPS (docker compose).

## Où trouver quoi

| Besoin | Fichier |
| :--- | :--- |
| Schéma BDD (source de vérité) | `db/init.sql` |
| Routes et modèle de données du socle | `docs/infos.md` |
| Fonctionnalités, MVP, contraintes, algos du groupe 3 | `docs/Document de cadrage Groupes EDT.md` |
| Cadrage de l'enseignant | `docs/document_cadrage_M2_2026_2027_projet_SAE.md` |
| Plan complet des 4 groupes | `docs/Plan_Projet_M2.md` : images base64, **lire par plage de lignes** (groupe 3 : l. 247-483) |
| Métriques et rétrospectives | `docs/metriques.md`, `docs/retros/sprint-N.md` |
| Journal IA et trailers | `journal/README.md` |

## Règles

### Toujours

- Avant toute modification, check état des branches, créer une branche `<type>/<nom>` (`feature/`, `fix/`, `docs/`…) si pas déjà fait, puis ouvrir une PR vers `dev`. La PR `dev` → `main` se fait seulement sur demande.
- Toute modification de `db/init.sql` ou du contrat d'API va dans le même commit/PR qu'une ligne de `docs/CHANGELOG-schema-api.md` (statut `proposé`).
- Langue : titres et descriptions de PR en français ; code, identifiants, commentaires, messages de commit et noms de branches en anglais. Les clés des trailers (`IA: genere`, `IA: retouche`, `Corrige:`) restent telles quelles, car `journal/stats.py` les lit.
- Commits en Conventional Commits (`.gitmessage`) avec le trailer d'origine : `IA: genere` (code généré commité tel quel), `IA: retouche` (corrections à la main, commit séparé), aucun trailer pour le code écrit à la main. Un fix de bug porte `Corrige: <sha du commit fautif>`.
- Sécurité, avant d'écrire du code et en relisant le diff :
  - SQL toujours paramétré via `query(sql, params)`, jamais de f-string ni de concaténation ;
  - chaque route vérifie le JWT et le rôle requis (RBAC), et un utilisateur n'accède qu'à ses propres données (notes, préférences, disponibilités) ;
  - entrées validées par des modèles Pydantic, imports CSV compris ;
  - mots de passe hachés en bcrypt ; aucun secret, token ou mot de passe dans le code, les logs ou les réponses d'API.
- Une ligne par tâche dans `journal/ia.csv`, ajoutée en fin de fichier. Module `infra-agent` pour le travail sur l'architecture agentique elle-même.
- Les scripts de `journal/` doivent tolérer les données manquantes : les conventions ne sont pas suivies par tout le monde, et une partie de l'équipe n'a pas Claude Code.
- Documents pour l'enseignant : dans `rapport/`, en Typst, avec le gabarit `rapport/template.typ` et la bibliographie `rapport/refs.bib` (IEEE). Chaque source est vérifiée, jamais inventée. L'enseignant note le recul critique plus que le résultat, et le rapport compare deux manières d'utiliser l'IA (classique et agentique), pas l'humain contre l'IA.

### Algorithmes de génération (glouton/coloration de graphe/recuit simulé/...)

- Ne pas livrer un algorithme que l'équipe ne comprend pas : concevoir avec l'humain, et documenter la complexité, les limites et les alternatives.
- Garder l'historique des versions de chaque algorithme.
- L'application n'appelle pas de LLM pour générer les emplois du temps.

### Demander avant

- `docker compose down -v`, ou toute autre commande qui supprime des données.
- Ajouter une dépendance.
- Modifier ce qui est partagé : schéma ou routes du socle (portée `commun`), contrat d'API EDT commun avec le groupe 2 (portée `projet B`).

### Jamais

- Committer `.env` ou un secret.
- Pousser directement sur `main` ou `dev`.

## Équipe

- DFS : Clément (référent API), Simon, Thibaut. Auth, API, front.
- DE : Daniel (référent Data), Thomas. BDD, import CSV, génération des emplois du temps, générateur de jeux de données (sert aussi au benchmark M9).

Un référent coordonne, mais il n'est pas le seul à toucher à son domaine. Les validations du changelog se font entre ces personnes.
