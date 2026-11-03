# Socle Commun

**Back :** FastAPI  
**Front :** Propre à chacun  

---

## API

### Authentification & Utilisateurs

| Endpoint | Description |
| :--- | :--- |
| `POST /auth/login`<br>`POST /auth/logout` | Vérification des identifiants et génération du JWT (access + refresh) |
| `POST /auth/refresh` | Renouvellement du token |
| `GET /users/me` | Infos et rôles de l'utilisateur connecté |
| `GET /users`<br>`POST /users`<br>`PUT /users/{user_id}`<br>`DELETE /users/{user_id}`<br>`PUT /users/{user_id}/roles`<br>`GET /roles` | Gestion des utilisateurs et rôles (Admin) |

### Structure pédagogique & Salles

| Catégorie | Endpoints | Description |
| :--- | :--- | :--- |
| **Années & Semestres** | `GET/POST /academic-years`<br>`GET/PUT /academic-years/{id}`<br>`GET/POST /academic-years/{id}/semesters`<br>`PUT/DELETE /semesters/{id}` | Gestion des années académiques et semestres |
| **Filières & Matières** | `GET/POST /programs`<br>`GET/PUT /programs/{id}`<br>`GET/POST /programs/{id}/subjects`<br>`GET/PUT/DELETE /subjects/{id}` | Gestion des filières et des matières associées |
| **Volumes horaires** | `GET/POST /subjects/{id}/volumes`<br>`PUT/DELETE /subject-volumes/{id}` | Gestion des volumes horaires par matière |
| **Groupes** | `GET/POST /groups`<br>`GET/PUT/DELETE /groups/{id}`<br>`GET/POST/DELETE /groups/{id}/students` | Gestion des groupes d'étudiants |

---

## Modèle de données

### 1. Socle Commun (Authentification, Utilisateurs & Rôles)
* `roles` (`id`, `code`, `label`)
* `users` (`id`, `last_name`, `first_name`, `email`, `password_hash`, `is_active`, `created_at`)
* `user_roles` (`user_id`, `role_id`)
* `audit_logs` (`id`, `actor_user_id`, `action`, `entity`, `entity_id`, `payload`, `created_at`)

### 2. Cœur Pédagogique (Scolarité & Groupes)
* `academic_years` (`id`, `label`, `start_date`, `end_date`)
* `semesters` (`id`, `label`, `academic_year_id`, `start_date`, `end_date`)
* `programs` (`id`, `name`, `level`)
* `subjects` (`id`, `code`, `title`, `program_id`, `semester_id`)
* `session_types` (`id`, `code`, `label`, `bg_color`, `text_color`)
* `subject_volumes` (`id`, `subject_id`, `session_type_id`, `planned_hours`)
* `groups` (`id`, `name`, `group_type`, `program_id`, `academic_year_id`, `parent_group_id`)
* `student_groups` (`user_id`, `group_id`)

### 3. Salles & Équipements
* `rooms` (`id`, `name`, `capacity`, `room_type`, `building`, `floor`)
* `equipments` (`id`, `label`)
* `room_equipments` (`room_id`, `equipment_id`, `quantity`)
* `room_unavailabilities` (`id`, `room_id`, `start_time`, `end_time`, `reason`)

### 4. Planification des Séances & Contraintes (EDT)
* `sessions` (`id`, `subject_id`, `session_type_id`, `room_id`, `start_time`, `end_time`, `status`, `comment`, `recurrence_group_id`)
* `session_teachers` (`session_id`, `teacher_id`, `is_primary`)
* `session_groups` (`session_id`, `group_id`)
* `user_unavailabilities` (`id`, `user_id`, `start_time`, `end_time`, `reason`)
* `teacher_preferences` (`id`, `teacher_id`, `subject_id`, `day_of_week`, `time_slot`, `priority`, `comment`)

### 5. Espace Personnel & Synchronisation
* `user_session_notes` (`id`, `user_id`, `session_id`, `content`, `updated_at`)
* `calendar_syncs` (`id`, `user_id`, `provider`, `export_token`, `last_sync_at`)
* `notifications` (`id`, `user_id`, `session_id`, `type`, `channel`, `content`, `sent_at`, `read_at`)