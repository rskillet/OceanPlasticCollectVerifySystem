# F1 · Accounts & access (backend)

**Owner:** Wongsathorn Sereephap · **Frontend:** `client/src/features/f1_accounts/` · **Tests:** `server/tests/f1_accounts/`

Sign-in with a session cookie, account requests approved by an admin, user management, profile, and the role check every other feature relies on.

| File | Purpose |
|---|---|
| `router.py` | API routes (`/api/auth/*`, `/api/admin/requests/*`, `/api/admin/users/*`) |
| `schemas.py` | Pydantic request/response models (`...In` / `...Out`) |
| `models.py` | SQLModel tables `users` (DM-1) and `sessions` (DM-4) |
| `service.py` | Business logic - reads and writes the two tables through the request's database session |
| `dependencies.py` | `get_current_user`, `CurrentUser`, `require_role` – **used by all features** |
| `seed.py` | Default admin (`admin`, FR-1.9) + demo users, all with password `password123`; added once when the database is empty |

**Status (2026-11-18):** all endpoints in `router.py` work, the F1 screens use them, and the data is stored in PostgreSQL, so accounts and sign-ins survive a restart. Tests: `docker compose exec backend python -m pytest tests/f1_accounts -vv`.

Passwords are stored as plain text in `users.password` (team decision D8) and never returned by the API. The `sessions` table stores only a SHA-256 hash of each session cookie.

**Spec:** FR-1.1 – FR-1.10, BR-7, BR-8, BR-9, NFR-15 · **Figma:** flow 01, Users, Profile

Rules to remember: session-based auth, not JWT (FR-1.2) · generic error on failed sign-in (FR-1.1) · PENDING / REJECTED / SUSPENDED users cannot sign in (BR-8) · suspending ends all sessions, users are never deleted (BR-7) · ADMIN is never offered at registration (BR-9).
