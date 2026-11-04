# Grille de métriques — Groupe 3 (EDT, agentique)

Quatre axes d'évaluation : productivité, qualité logicielle, qualité de processus, qualité finale. Chaque métrique indique sa source et quand elle devient mesurable. Les numéros `M1`–`M10` renvoient aux 10 métriques du plan de projet.

Légende : ✅ en place · 🔧 à brancher en CI · 🚀 au déploiement · 📋 manuel

## 1. Productivité et usage de l'IA

| Métrique | Source | État |
| :--- | :--- | :--- |
| Temps réel par rapport au temps estimé, par tâche (M2) | `journal/ia.csv` | ✅ |
| Nombre de tâches, réparties par personne et par module | `ia.csv` → `stats.py` | ✅ |
| Nombre de commits par personne et par origine (généré, retouché, manuel) | git → `stats.py` | ✅ |
| Interventions humaines par tâche, taux de réussite sans intervention (M1) | `ia.csv` | ✅ |
| Temps de mise en place, de revue et de correction du code IA (M3) | `ia.csv` | ✅ |
| Tours, tokens et coût (équivalent API) par tâche | `journal/tokens.py` | ✅ |
| Coût fixe de l'architecture agentique (module `infra-agent`) | `ia.csv` → `stats.py` | ✅ |
| Taux de retouche : lignes retouchées / lignes générées (M4) | trailers `IA:` | ✅ |
| Code IA modifié ou supprimé : part des lignes générées qui ne sont plus dans `HEAD` | `git blame` → `stats.py` | ✅ |
| Bugs par origine, pour 1000 lignes (M5) | trailer `Corrige:` | ✅ |

## 2. Qualité logicielle

Référence : **ISO/IEC 25010** (modèle de qualité du produit logiciel), en particulier la maintenabilité et la sécurité.

| Métrique | Outil | État |
| :--- | :--- | :--- |
| Couverture de tests, taux de mutation (M7) | pytest-cov, mutmut | 🔧 |
| Complexité cyclomatique (M8) | radon | 🔧 |
| Duplication (M8), ratio de dette technique (M6) | SonarCloud | 🔧 |
| Dette du code IA par rapport au code manuel | SonarCloud filtré par commits `IA:` | 🔧 |
| Vulnérabilités du code (Python) | bandit | 🔧 |
| Vulnérabilités des dépendances | pip-audit, `npm audit` | 🔧 |
| Respect de l'architecture (pas d'import interdit entre couches) | import-linter | 🔧 |
| Conformité au contrat d'API OpenAPI | schemathesis | 🔧 |

## 3. Qualité de processus

Référence : **métriques DORA** (DevOps Research and Assessment), complétées par le suivi des tâches et la coopération.

| Métrique | Source | État |
| :--- | :--- | :--- |
| Fréquence de déploiement | GitHub Actions (déploiements sur le VPS) | 🚀 |
| Délai entre commit et production (*lead time for changes*) | GitHub Actions | 🚀 |
| Taux d'échec des changements (déploiement suivi d'un correctif ou d'un revert) | GitHub Actions + trailer `Corrige:` | 🚀 |
| Temps de restauration après incident | issues `incident` | 🚀 |
| Délai de revue des PR, taux d'acceptation | GitHub (PR) | 🔧 |
| Coopération : délai de validation et taux d'acceptation dans le changelog schéma/API (M10) | `docs/CHANGELOG-schema-api.md` | 📋 |
| Vélocité : tâches terminées par sprint | issues / tableau GitHub Projects | 📋 |

## 4. Qualité finale

Référence : **ISO/IEC 25010** (adéquation fonctionnelle, performance, utilisabilité, fiabilité, sécurité).

| Métrique | Méthode | État |
| :--- | :--- | :--- |
| Fonctionnalités : part du MVP livrée et couverte par des tests | checklist du MVP + tests e2e | 📋 |
| Qualité de l'algorithme : contraintes dures violées (doit valoir 0), score des contraintes souples (trous, préférences, équilibre) (M9) | script de benchmark | 🔧 |
| Temps d'exécution de l'algorithme selon la taille des données (M9) | script de benchmark | 🔧 |
| Performance de l'API : latence p95, débit | k6 ou locust | 🚀 |
| Robustesse : taux d'erreur sous charge, comportement sur entrées invalides | k6/locust, schemathesis | 🚀 |
| Utilisabilité : score SUS (System Usability Scale, 10 questions, sur 100) | questionnaire, environ 5 utilisateurs | 📋 |
| Performance et accessibilité du front | Lighthouse | 🔧 |
| Sécurité en production : en-têtes HTTP, HTTPS | Mozilla Observatory | 🚀 |

## 5. Comment améliorer

Une rétrospective courte par sprint dans `docs/retros/sprint-N.md` :

1. Ce qui a marché
2. Ce qui a coincé (avec les chiffres du sprint : `python journal/stats.py`)
3. Ce qu'on change dans l'architecture agentique (prompts, skills, sous-agents, conventions)

Les retros servent de matière première pour la partie « recul » du rapport : comment le processus a évolué et pourquoi.
