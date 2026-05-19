# ShieldTB Backend Architecture

## Starting Shape

ShieldTB starts as a Django modular monolith. The platform is clinically
ambitious, but the first backend should optimize for correctness, auditability,
and fast iteration rather than distributed-system complexity.

Service extraction can happen later around natural seams:

- ML inference
- notifications
- analytics
- interoperability/FHIR adapters

## Week 1 Decisions

- Runtime: Python 3.12
- Web framework: Django 5.2 family
- API framework: Django REST Framework
- Database: PostgreSQL, with PostGIS planned for geospatial work
- Async jobs: Celery + Redis planned for Week 6-8 workflow and reminder jobs
- Deployment: Docker Compose for development
- Architecture: modular monolith with app-level domain boundaries

Architecture decision records live in `docs/adr/`. These capture intentional
MVP compromises and the triggers for revisiting them.

Current ADRs:

- `0001-database-backed-access-token-blocklist.md`
- `0002-postgresql-as-primary-database.md`

## Initial Domains

- `accounts`: users, roles, facility assignment
- `facilities`: dispensaries, hospitals, labs, community units
- `patients`: patient registry and consent anchor
- `clinical`: encounters and structured intake
- `risk`: transparent rules-based scoring, later ML-backed scoring
- `households`: contact tracing and household contact status
- `tasks`: CHW and clinical workflow tasks
- `notifications`: SMS, WhatsApp, USSD, and in-app notification records
- `audit`: access and mutation event records
- `analytics`: precomputed facility metrics

## AI Reality Check

The first AI-like component is an explainable rules engine. That is intentional:
the platform needs validated structured data before supervised ML is clinically
or operationally credible.

## Near-Term Build Order

1. Auth, users, roles, and facility scoping
2. Patient registry and consent recording
3. Clinical intake APIs
4. Risk scoring API with score explanations
5. Household/contact tracing workflow
6. CHW task assignment
7. Notification provider abstraction
8. Dashboards and analytics endpoints

## API Artifacts

OpenAPI is the source of truth for API-sharing artifacts. Generate it with:

```bash
cd backend
python manage.py export_api_artifacts
```

This produces a schema plus ready-to-share Postman files in
`backend/docs/generated/`.
