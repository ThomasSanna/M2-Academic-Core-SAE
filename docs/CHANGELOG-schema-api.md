# Changelog du schéma de données et du contrat d'API

Toute modification de `db/init.sql` ou du contrat d'API passe par une ligne ici. Sert à tracer la coopération (métrique M10 : délai de validation, taux d'acceptation).

- **Statut** : `proposé`, `accepté`, `refusé`
- **Portée** : `groupe 3` (notre fork uniquement), `projet B` (avec le groupe 2), `commun` (les 4 groupes)
- **Délai** : jours entre la proposition et la décision

| Date proposition | Proposé par | Portée | Type | Changement | Raison | Validé par | Date décision | Statut |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| | | | schéma / API | | | | | |

## Écarts connus à arbitrer

Écarts entre `db/init.sql` et le plan du groupe 3, à passer en ligne `proposé` ci-dessus quand on les traite :
- `calendar_syncs` : le plan prévoit `external_calendar_id` et `sync_token`.
- `semesters` : le plan n'a pas de dates.
- `audit_logs` : absent du plan.
