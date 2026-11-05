# Reste à faire — Groupe 3

Échéances : soutenance en janvier 2027, rapport une semaine avant (dates exactes à confirmer).

## Décisions à prendre

- [ ] Contrat d'API EDT avec le groupe 2 : séances, génération, disponibilités, vues. Rien n'est défini au-delà du socle (`docs/infos.md`).
- [ ] Base partagée et déploiement final : où, qui héberge (« décidé avant la phase de dev » selon le cadrage).
- [ ] Données manquantes pour le MVP : jours fériés, créneaux horaires possibles, salles spécialisées TP (`room_type` ou `equipments` ?).
- [ ] Écarts de schéma déjà listés dans `CHANGELOG-schema-api.md`.
- [ ] Quand utiliser l'ORM, quand utiliser du SQL brut (#9).
- [ ] Organisation : sprints, tableau GitHub Projects, rétros dans `docs/retros/`.

## Backend (MVP)

- [ ] Auth JWT (login, refresh, logout), `get_current_user`, RBAC.
- [ ] Erreurs communes 403 / 404 / 409.
- [ ] CRUD du socle : users, rôles, années, semestres, filières, matières, volumes, groupes, inscriptions.
- [ ] Salles et indisponibilités, disponibilités et préférences des profs.
- [ ] Séances : création, modification, suppression avec détection de conflits (salle, prof, groupe, capacité), en une transaction.
- [ ] Import CSV (salles, groupes, matières, profs).
- [ ] Vues filtrées : groupe, prof, salle ; semaine, jour.
- Hors MVP : notes perso, export iCal, notifications, historique des modifications, recherche.

## Génération (DE)

- [ ] Modèle du problème en mémoire dans `backend/scheduling/`.
- [ ] Validateur : contraintes dures violées (doit valoir 0), score des contraintes souples.
- [ ] Générateur de jeux de données de tailles croissantes.
- [ ] V1 glouton, V2 coloration de graphe, V3 recuit simulé : complexité, limites, historique des versions.
- [ ] Benchmark M9 : qualité et temps selon la taille.
- Questions :
  - Granularité des créneaux : heure, demi-heure ?
  - Générer une semaine type répétée, ou tout le semestre ?
  - Examens, rattrapages, changements en cours de semestre : générés ou saisis à la main ?
  - Correction manuelle après génération : comment garantir qu'elle ne casse pas les contraintes ?

## Front (DFS)

- [ ] Choix du framework, justifié.
- [ ] Types TypeScript générés depuis `/openapi.json`.
- [ ] Écrans :
  - login ;
  - calendrier semaine/jour avec couleurs par type ;
  - multi-vues ;
  - détail d'un créneau ;
  - écrans admin : séances, import, génération.

## Qualité, CI, déploiement

- [ ] CI GitHub Actions : pytest et couverture, radon, mutmut, bandit, pip-audit (voir `metriques.md`).
- [ ] SonarCloud : dette, duplication, code IA comparé au code manuel.
- [ ] Déploiement : images ghcr, VPS, HTTPS, secrets (JWT, BDD), pas de compte de démo en production.
- [ ] Tests e2e, charge (k6/locust), Lighthouse, questionnaire SUS.

## Mesure et architecture agentique

- [ ] Une ligne de journal par tâche, avec l'estimation notée **avant** de commencer.
- [ ] `tokens.py` pour les autres outils, dont OpenCode (#8).
- [ ] Formaliser l'architecture agentique : sous-agents, skills, hooks, et ce que chacun apporte (coût fixe `infra-agent`).
- [ ] Une rétro par sprint.

## Rapport et soutenance

- [ ] `rapport/etat-de-l-art.typ:52` cite encore `CLAUDE.md` : remplacer par `AGENTS.md`, puis recompiler.
- [ ] Comparaison avec le groupe 2 : quelles métriques communes, et leurs données sont-elles comparables (même format de journal) ?
- [ ] Sujets proposés dans l'issue #5 :
  - confidentialité et rétention des données envoyées aux IA ;
  - écologie de l'usage de l'IA ;
  - éthique de l'application.
- [ ] Partie algorithmique : choix, comparaison, résultats du benchmark.
