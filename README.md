# ShieldTB Platform

Backend-first implementation of ShieldTB Kenya: a clinical workflow and risk
stratification platform for TB screening, household contact tracing, and
differentiated care.

## Week 1 Scope

- Django modular monolith backend scaffold
- PostgreSQL-ready configuration
- Docker Compose development environment
- Initial health-tech domain boundaries
- Core data model drafts for facilities, patients, clinical intake, risk,
  household tracing, workflow tasks, notifications, and audit logs

## Week 2 Scope

- Secure JWT login, refresh, logout, and current-user endpoints
- HttpOnly auth cookies with short-lived access tokens
- Rotating refresh tokens with blacklist support
- Database-backed access-token `jti` revocation for logout
- Facility and user API foundations with role-based permissions
- Base audit-event helper with sensitive metadata redaction
- GitHub Actions CI for `feature/**`, `develop`, and `main`

## Local Development

```bash
cd backend
cp .env.example .env
docker compose up --build
```

The API will run at `http://localhost:8000/`.

Run checks:

```bash
cd backend
docker compose run --rm api ruff check --no-cache .
docker compose run --rm api python manage.py check
docker compose run --rm api pytest
```

## Architecture

Start as a modular monolith. Split into services only when real scale,
operational isolation, or team boundaries justify it.
