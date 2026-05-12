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

## Local Development

```bash
cd backend
cp .env.example .env
docker compose up --build
```

The API will run at `http://localhost:8000/`.

## Architecture

Start as a modular monolith. Split into services only when real scale,
operational isolation, or team boundaries justify it.

