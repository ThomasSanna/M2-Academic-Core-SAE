# Contexte projet — SAE M2 DFS&DE (Groupe 3, EDT, **agentique**)

## Cadre
- Projet de génie logiciel M2 : SIS/ERP éducatif, sous-projets A (répartition des services) et B (**emplois du temps**, notre cas).
- 4 groupes, 2 par sous-projet : « classique » (IA ponctuelle, pas d'agent autonome) vs « agentique » (architecture d'agents, le moins de code à la main possible). **Nous = Groupe 3, B, agentique.** Le groupe 2 est l'équivalent classique sur les EDT (mêmes objectifs).
- Évaluation : recul > résultat. Veille techno sourcée, métriques, critique du code IA, dette technique, qualité de la coopération (changelog schéma/API : qui propose, qui valide, quelle date).
- Phase dev depuis mi-octobre 2026 : **journalisation obligatoire** pour mesurer l'impact de l'IA (interventions humaines, temps, retouches, etc.).
- Pas de "humain vs IA" : on compare deux manières d'utiliser l'IA.
- Les algorithmes (glouton, coloration de graphe, recuit simulé) ne doivent PAS être délégués à un LLM sans compréhension : concevoir, justifier (complexité, limites, alternatives), garder l'historique des versions. L'appli n'a pas à embarquer d'IA ; un appel LLM ne remplace pas l'algo.
- Équipe : DFS = Clément (LORIEAU, référent API), Simon, Thibaut ; DE = Thomas, Daniel (GUERRA, référent Data, l'utilisateur). Un référent coordonne, il n'est pas seul à toucher BDD/API. Le front est géré par les DFS (framework pas encore tranché).
- Outillage : pas homogène dans l'équipe. Daniel : Claude Code uniquement (sous-agents, skills) ; d'autres n'ont pas Claude. Le journal doit rester utilisable sans Claude Code (colonne `outil`).
- Répartition : DE (Daniel, Thomas) plutôt BDD, import CSV, algorithme de génération ; DFS (Clément, Simon, Thibaut) plutôt auth, API, front. Un peu de transversal quand même.
- Git : `main` (stable), `dev` (intégration), branches `feature/<nom>` ; PR `feature/*` → `dev` → `main`.
- Données : pas de données réelles, il faudra un générateur de jeux de données (tailles variables, sert aussi au benchmark M9).
- Schéma commun (`db/init.sql`) : on l'étend si besoin, en traçant chaque changement dans `docs/CHANGELOG-schema-api.md`.
- Adhésion aux conventions (journal, trailers) non garantie : rester tolérant aux données manquantes dans les scripts.
- Planning : soutenance en janvier 2027 ; rapport au plus tard une semaine avant.
- Intégration avec le groupe 2 : chacun avance de son côté, intégration plus tard (pas prioritaire).
- BDD non partagée pour l'instant : chaque groupe a sa propre base.
- Socle commun aux 4 groupes : cahier des charges global, BDD, métriques génériques, contrat d'API auth/rôles, repo commun. Les sous-groupes d'un même projet partagent le contrat d'API EDT ; chacun l'implémente.

## Stack (imposée)
FastAPI (Python) · PostgreSQL 16 · JWT + rôles (RBAC) · Docker compose · pytest + CI GitHub Actions · ghcr. Front : React/Next.js + Tailwind + shadcn/ui.

## Repo
- Ce repo est un fork du starter commun (même base de départ pour les 4 groupes).
- `backend/main.py` : API FastAPI minimale (`query(sql, params)` via psycopg, `/health`, `/roles`). Pas encore de JWT/bcrypt.
- `db/init.sql` : 24 tables + données de référence (rôles ADMIN/MANAGER/TEACHER/STUDENT, types CM/TD/TP/EXAM, admin `admin@example.com` / `admin1234`). Joué uniquement au 1er démarrage (`docker compose down -v` pour recréer).
- `docker-compose.yml` : db (monte `./db/init.sql`), backend (--reload), adminer (`--profile tools`).
- Lancer : `docker compose up --build` → API :8000 (`/docs`), Postgres :5432 (`sae`/`sae`/`sae`).
- `docs/` : voir ci-dessous.

## Documents pour l'enseignant (`rapport/`)
Tous les documents de type rapport destinés au prof vont dans `rapport/`, en Typst (gabarit commun `rapport/template.typ`, bibliographie commune `rapport/refs.bib`, style IEEE). Compiler : `typst compile rapport/<fichier>.typ`. Sources vérifiées et citées, jamais inventées.
- `etat-de-l-art.typ` : état de l'art sur les architectures agentiques.

## Docs de travail (`docs/`)
- `infos.md` : socle commun (routes + modèle de données).
- `document_cadrage_M2_2026_2027_projet_SAE.md` : cadrage de l'enseignant.
- `Plan_Projet_M2.md` : sections Groupes 1-4 + socle commun (très lourd, images base64 : lire par plage de lignes ; Groupe 3 = l. 247-483).
- `Document de cadrage Groupes EDT.md` : cadrage EDT (équivalent de la section Groupe 3).

## Fonctionnalités du groupe 3
- Rôles : **Étudiant** (filtres agrégés salles/profs/classes, notes perso par créneau, message à un prof, export EDT) ; **Professeur** (modifier/supprimer un créneau avec permission sysadmin, mail à une classe, EDT regroupé) ; **Admin** (modifie/ajoute des créneaux, lance la génération) ; **SysAdmin** (comptes, rôles, config, supervision, historique des modifications).
- Entrées : salles/capacités, groupes, disponibilités profs, types de séance (CM/TD/TP), durées, créneaux possibles.
- Contraintes dures : pas de double réservation (salle, prof, groupe), capacité des salles, salles spécialisées pour les TP. Souples : préférences profs, pas de trous, répartition équilibrée sur la semaine.
- Cas particuliers : examens, rattrapages, jours fériés, changements en cours de semestre. Question ouverte : correction manuelle sans casser les contraintes.
- Autres : codes couleur par type, style Google Calendar/Celcat, recherche avancée (prochain cours/examen), détail créneau (matière, prof, salle, groupe, effectif, matériel, commentaire), multi-vues (promo/groupe/prof/salle/matière), import/export calendriers (Google/Apple/Samsung), notifications email/SMS sur changement ou absence, accès sans reconnexion fréquente (token/cookies).
- **MVP** : auth JWT + rôles ; import CSV (salles, groupes, matières, profs) ; calendrier jours fériés ; disponibilités profs ; génération automatique avec contraintes ; CRUD séance (admin) avec détection de conflits ; vue calendrier semaine/jour avec couleurs ; multi-vues ; détail créneau.
- Algorithmes, par ordre : 1) glouton, 2) coloration de graphe, 3) recuit simulé.

## Modèle de données
Voir `db/init.sql` (source de vérité) et `docs/infos.md`. Blocs : auth (roles, users, user_roles, audit_logs) · pédagogie (academic_years, semesters, programs, subjects, session_types, subject_volumes, groups, student_groups) · salles (rooms, equipments, room_equipments, room_unavailabilities) · séances (sessions, session_teachers, session_groups, user_unavailabilities, teacher_preferences) · perso (user_session_notes, calendar_syncs, notifications).
Écarts connus avec le plan Groupe 3 : `Calendar_Sync` y a `external_calendar_id` + `sync_token` ; `Semester` n'y a pas de dates ; `audit_logs` absent du plan. À harmoniser via le changelog.

## API
- Socle : `POST /auth/login|logout|refresh`, `GET /users/me`, CRUD `/users` + `PUT /users/{id}/roles`, `GET /roles`.
- Pédagogie : `/academic-years` (+ `/semesters`), `/programs` (+ `/subjects`), `/subjects/{id}/volumes`, `/subject-volumes/{id}`, `/groups` (+ `/students`).
- Salles : `GET/POST /rooms`, `POST /rooms/{id}/unavailabilities`.
- **Pas encore spécifié** : séances (CRUD, conflits), génération d'EDT, disponibilités/préférences, notes, notifications, export/sync calendrier, import CSV, audit.

## Métriques à suivre (10)
1. Interventions humaines par tâche, taux de réussite sans intervention · 2. Temps réel vs estimé · 3. Temps de mise en place/revue/correction du code IA · 4. Taux de retouche (code généré modifié à la main avant fusion) · 5. Défauts/1000 lignes par module et sprint · 6. Ratio de dette technique · 7. Couverture de tests et taux de mutation · 8. Complexité cyclomatique et duplication · 9. Qualité de la solution algorithmique et temps d'exécution selon la taille · 10. Coopération (délai de validation, taux d'acceptation dans le changelog).

## Conventions de travail
- Réponses courtes, en français si l'utilisateur écrit en français.
- Toute modif du schéma BDD ou du contrat d'API doit être consignée dans `docs/CHANGELOG-schema-api.md`.
- Modèle de commit avec rappel des trailers : `git config commit.template .gitmessage`.
- Journaliser l'usage de l'IA dans `journal/ia.csv` (une ligne par tâche, voir `journal/README.md`) ; tours/tokens/coût d'une tâche : `python journal/tokens.py --since "AAAA-MM-JJ HH:MM"` ; agrégation : `python journal/stats.py`. Module `infra-agent` pour le travail sur l'architecture agentique elle-même (coût fixe).
- Commits : trailer `IA: genere` pour le code généré commité tel quel, `IA: retouche` pour les corrections manuelles (commit séparé), aucun trailer pour le code écrit à la main. Un fix de bug porte `Corrige: <sha du commit fautif>`. Sert au taux de retouche et aux bugs par origine.
- Grille complète des métriques (productivité, qualité logicielle ISO 25010, processus DORA, qualité finale, retros) : `docs/metriques.md`. Rétrospective par sprint dans `docs/retros/sprint-N.md`.
- Métriques 5-8 : à calculer en CI (pytest-cov, mutmut, radon/SonarCloud), pas dans le journal.

## Déploiement
VPS appartenant à l'équipe : docker compose + reverse proxy (Caddy, HTTPS) ; images sur ghcr, déploiement par GitHub Actions sur push `main`. Pas encore mis en place.
