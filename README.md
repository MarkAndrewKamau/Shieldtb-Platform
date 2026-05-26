# ShieldTB Platform

A clinical workflow and risk stratification platform for tuberculosis screening,
household contact tracing, and differentiated care, built for the Kenyan public
health context.

ShieldTB digitises the path a patient and their contacts travel through the TB
care cascade: facility-scoped patient registration, structured clinical intake,
transparent risk scoring, household contact tracing, community health worker
(CHW) task assignment, notifications, and facility-level analytics. Every
sensitive action is audited.

This repository now contains:

- a Django backend service under [`backend/`](backend/)
- a mobile app under [`apps/mobile/`](apps/mobile/)
- shared frontend packages under [`packages/`](packages/)

The backend is implemented as a Django modular monolith with a REST API,
designed so that individual domains can be extracted into independent services
later, only when real scale or team boundaries justify the cost. The frontend
starts mobile-first for CHW workflows, while the web dashboard layer is planned
to follow on the same API contract.

---

## Table of Contents

- [Why This Design](#why-this-design)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Domain Model](#domain-model)
- [API Surface](#api-surface)
- [Security Model](#security-model)
- [Engineering Tradeoffs](#engineering-tradeoffs)
- [Scaling Roadmap](#scaling-roadmap)
- [Local Development](#local-development)
- [Testing and Continuous Integration](#testing-and-continuous-integration)
- [API Artifacts](#api-artifacts)
- [Project Structure](#project-structure)
- [Delivery History](#delivery-history)

---

## Why This Design

ShieldTB handles clinical data, so the backend optimises for **correctness,
auditability, and fast iteration** before distributed-system sophistication.

Three principles drive the design:

1. **Start as a modular monolith.** Domain boundaries are enforced at the Django
   app level, not at the network level. Splitting into services is a deliberate
   future step with documented triggers, not a default.
2. **Make intentional MVP compromises, and write them down.** Every shortcut
   that trades long-term scale for short-term delivery speed is captured as an
   Architecture Decision Record (ADR) in [`docs/adr/`](docs/adr/), together with
   the concrete conditions that should force a revisit.
3. **Earn the right to use ML.** The first "AI-like" component is an explainable
   rules engine. Supervised models are only credible once the platform has
   validated, structured clinical data to train on.

The result is a system that is simple to operate today and has a clear,
pre-planned path to scale.

---

## Architecture

ShieldTB is a single deployable Django service backed by PostgreSQL. Each
business domain is an isolated Django app with its own models, serializers,
views, and tests.

```
                         HTTP / REST (JSON)
                                 |
                     +-----------------------+
                     |   Django + DRF API    |
                     |  (modular monolith)   |
                     +-----------------------+
                                 |
   accounts  facilities  patients  clinical  risk  households
   tasks     notifications  analytics  audit  core
                                 |
                     +-----------------------+
                     |      PostgreSQL       |
                     +-----------------------+
```

Future service-extraction seams are already identified: ML inference,
notifications, analytics, and interoperability/FHIR adapters. Until the platform
reaches the scale that justifies that operational overhead, these remain
in-process modules behind stable interfaces.

The full architecture narrative lives in [`docs/architecture.md`](docs/architecture.md).

---

## Technology Stack

| Concern            | Choice                                              |
| ------------------ | --------------------------------------------------- |
| Language           | Python 3.12                                         |
| Web framework      | Django 5.2                                          |
| API framework      | Django REST Framework                               |
| Authentication     | DRF SimpleJWT with rotating refresh tokens          |
| API schema         | drf-spectacular (OpenAPI 3)                         |
| Database           | PostgreSQL 16 (PostGIS planned for geospatial work) |
| Database access    | psycopg 3, `dj-database-url` configuration          |
| Application server | Gunicorn                                            |
| Local environment  | Docker Compose                                      |
| Linting            | Ruff                                                |
| Testing            | pytest with `pytest-django`                         |
| CI                 | GitHub Actions                                      |

Mobile frontend stack:

- Expo + React Native
- Expo Router
- TanStack Query
- Zustand
- React Hook Form
- Expo Secure Store

Asynchronous infrastructure (Celery and Redis) is intentionally **not** a
current dependency. See [Engineering Tradeoffs](#engineering-tradeoffs) for the
reasoning and the triggers for introducing it.

---

## Domain Model

Each domain is a self-contained Django app under [`backend/apps/`](backend/apps/).

| App             | Responsibility                                                        | Core models                          |
| --------------- | --------------------------------------------------------------------- | ------------------------------------- |
| `accounts`      | Users, roles, facility assignment, access-token revocation            | `User`, `AccessTokenBlocklist`        |
| `facilities`    | Dispensaries, hospitals, labs, and community units                    | `Facility`                            |
| `patients`      | Patient registry and the consent anchor for clinical data             | `Patient`                             |
| `clinical`      | Clinical encounters and structured intake records                     | `ClinicalEncounter`, `ClinicalIntake` |
| `risk`          | Transparent rules-based risk scoring with score explanations          | `RiskAssessment`                      |
| `households`    | Household contact tracing and contact screening status                | `Household`, `HouseholdContact`       |
| `tasks`         | CHW and clinical workflow tasks                                       | `WorkflowTask`                        |
| `notifications` | Notification records and a channel-agnostic delivery abstraction      | `Notification`                        |
| `analytics`     | Live facility summaries and precomputed daily metric snapshots        | `FacilityDailyMetric`                 |
| `audit`         | Access and mutation event records with sensitive-metadata redaction   | `AuditEvent`                          |
| `core`          | Shared base models and the OpenAPI/Postman artifact generator         | `TimeStampedModel`                    |

Notable domain behaviour:

- **Consent attribution.** Patient records carry consent attribution, and
  patient access is facility-scoped.
- **Automatic risk assessment.** A `RiskAssessment` is created automatically
  from clinical intake data, and the resulting score is explainable.
- **Workflow automation.** Registering a household automatically creates a
  household screening `WorkflowTask`; assigning that task notifies the CHW.

---

## API Surface

The API is versioned under `/api/v1/`. Authentication endpoints are grouped
under `/api/v1/auth/`; all domain resources are exposed through a DRF router.

**Authentication** (`/api/v1/auth/`)

| Endpoint    | Purpose                                               |
| ----------- | ----------------------------------------------------- |
| `signup/`   | Register a new user                                   |
| `login/`    | Obtain access and refresh tokens                      |
| `refresh/`  | Rotate the refresh token and issue a new access token |
| `logout/`   | Revoke the current access token and refresh token     |
| `me/`       | Return the authenticated user                         |

**Domain resources** (`/api/v1/`)

| Resource                              | Description                                |
| ------------------------------------- | ------------------------------------------ |
| `facilities/`                         | Facility registry                          |
| `users/`                              | User management                            |
| `patients/`                           | Facility-scoped patient registry           |
| `clinical/encounters/`                | Clinical encounters                        |
| `clinical/intakes/`                   | Structured clinical intake                 |
| `risk-assessments/`                   | Read-only risk assessments                 |
| `households/`                         | Households under tracing                   |
| `household-contacts/`                 | Household contacts and screening status    |
| `workflow-tasks/`                     | CHW and clinical workflow tasks            |
| `notifications/`                      | Read-only in-app notifications             |
| `analytics/facility-summaries/`       | Live facility summary metrics              |
| `analytics/daily-metrics/`            | Daily facility metric snapshots            |

**Operational and documentation endpoints**

| Endpoint               | Purpose                          |
| ---------------------- | -------------------------------- |
| `health/`              | Liveness/health check            |
| `api/schema/`          | OpenAPI 3 schema                 |
| `api/schema/swagger/`  | Swagger UI                       |
| `admin/`               | Django administration site       |

---

## Security Model

Authentication uses short-lived access tokens and rotating refresh tokens.
Full detail is in [`docs/security.md`](docs/security.md); the key controls are:

- **Short-lived access tokens.** Access tokens expire after 15 minutes; refresh
  tokens after 7 days.
- **Refresh-token rotation.** Refresh tokens rotate on use, and the previous
  token is blacklisted.
- **Revocable access tokens.** Each access token carries a `jti`; logout records
  it in a database-backed blocklist so a stolen token can be revoked before its
  natural expiry.
- **Client-specific token delivery.** Browser clients receive tokens through
  HttpOnly cookies with CSRF enforcement on unsafe requests. Native/mobile
  clients may explicitly request `auth_mode: "token"` and store the returned
  access/refresh pair in device secure storage.
- **Algorithm hardening.** The signing algorithm is fixed server-side. The
  `alg: none` attack is rejected by configuration and covered by tests; token
  headers never influence verification behaviour.
- **Minimal claims.** JWTs carry only identity and scoping claims (`sub`,
  `role`, `facility_id`, `iss`, `aud`, `iat`, `exp`, `jti`). Clinical data and
  sensitive PII are never placed in token payloads.
- **Redacted audit logging.** Audit events record actor, action, resource, IP,
  and user agent with sensitive metadata redacted. Authorization headers,
  cookies, tokens, and passwords are never written to logs or audit metadata.

---

## Engineering Tradeoffs

ShieldTB deliberately makes MVP-stage compromises that trade long-term scale for
delivery speed and operational simplicity. Each is recorded as an ADR with the
concrete conditions that should trigger a redesign.

### ADR 0001 — Database-backed access-token blocklist

The ideal high-throughput design is a Redis-backed blocklist keyed by `jti` with
automatic TTL expiry. For the MVP, Redis is not otherwise required, so token
revocation uses a PostgreSQL `AccessTokenBlocklist` model instead.

- **Why acceptable now:** access tokens already expire in 15 minutes; the
  implementation is simple, inspectable in Django admin, and immediately
  testable; pilot-scale write volume is low.
- **Tradeoff:** every authenticated request performs a database existence
  check, and expired rows need periodic cleanup.
- **Revisit when:** the lookup becomes measurable in latency or load, Redis
  arrives for another reason, multiple services need shared revocation, or
  load testing for a county-level pilot begins.

### ADR 0002 — PostgreSQL as the primary database

PostgreSQL is used for development, CI, staging, and production. SQLite is
explicitly avoided, even for tests, to keep production parity and prevent subtle
behavioural differences.

- **Why:** strong transactional guarantees for clinical intake and risk
  scoring, a good fit for audit and reporting workloads, and a natural path to
  PostGIS for household tracing and hotspot mapping.
- **Tradeoff:** developers must run PostgreSQL locally (handled by Docker
  Compose).

### ADR 0003 — Synchronous in-app notifications first

Notifications use a first-class `Notification` model and a channel-agnostic
provider abstraction, but dispatch happens synchronously inside the web process.
There is no Celery or message queue yet.

- **Why acceptable now:** it produces real, auditable delivery records and a
  stable integration surface for future SMS and WhatsApp adapters, without
  introducing queue infrastructure before scheduled reminder workloads exist.
- **Tradeoff:** dispatch occurs during the request/response cycle; scheduled
  reminders are stored but not yet processed; retries and backoff are not
  implemented.
- **Revisit when:** scheduled reminders, external providers, retry policies, or
  latency-sensitive delivery become real requirements.

### ADR 0004 — Live facility analytics with manual daily snapshots

Analytics has two layers: live facility summaries computed directly from
transactional tables, and `FacilityDailyMetric` snapshots refreshed explicitly
for the current day through a management command or an admin/analyst-only API
action.

- **Why acceptable now:** it delivers usable dashboards immediately, keeps the
  logic close to existing domain models, and avoids a premature warehouse or
  scheduling stack. The snapshot model is a clean handoff point for later
  scheduled aggregation.
- **Tradeoff:** live summaries query transactional tables directly, and
  snapshots capture today's state rather than reconstructing full history.
- **Revisit when:** dashboard traffic pressures transactional queries, county or
  national rollups are needed, or reports require longer time-series windows.

---

## Scaling Roadmap

The current design is intentionally minimal. As data volume and operational
demands grow, these are the planned, pre-identified evolution steps:

| Area                | Today                                              | Planned at scale                                                            |
| ------------------- | -------------------------------------------------- | --------------------------------------------------------------------------- |
| Token revocation    | PostgreSQL `AccessTokenBlocklist` with cleanup     | Redis blocklist keyed by `jti` with automatic TTL expiry                    |
| Notifications       | Synchronous in-process dispatch, in-app channel    | Celery workers, Redis-backed queues, SMS/WhatsApp/USSD adapters with retries |
| Reminders           | Stored, dispatched on assignment                   | Celery-scheduled reminder jobs                                              |
| Analytics           | Live queries plus manual/API daily snapshots       | Celery-scheduled snapshots, materialized views, cohort and trend analytics  |
| Geospatial          | Standard relational data                           | PostGIS for household tracing and TB hotspot mapping                        |
| Risk scoring        | Explainable rules engine                           | Supervised ML inference, extractable as an independent service              |
| Architecture        | Modular monolith                                   | Service extraction along ML, notifications, analytics, and FHIR seams       |

Across every item, the public API contract and the application-facing service
interfaces are kept stable, so these are implementation changes rather than
breaking changes for API consumers.

---

## Local Development

The local environment runs the API and PostgreSQL through Docker Compose.

```bash
cd backend
cp .env.example .env
docker compose up --build
```

The API is then available at `http://localhost:8000/`.

The `.env.example` file documents every required setting, including the JWT
signing key, issuer, audience, and cookie policy. For non-trivial environments,
generate a strong signing key:

```bash
openssl rand -base64 32
```

Use distinct signing keys for development, staging, and production.

---

## Testing and Continuous Integration

The suite contains 34 tests across all ten domains, run with pytest against a
real PostgreSQL database.

Run the local checks:

```bash
cd backend
docker compose run --rm api ruff check --no-cache .
docker compose run --rm api python manage.py check
docker compose run --rm api pytest
```

GitHub Actions runs the [`CI` workflow](.github/workflows/) on pushes to `main`,
`develop`, and `feature/**` branches, and on pull requests into `main` and
`develop`. Each run, against a PostgreSQL 16 service, performs:

1. Ruff lint
2. Django system checks
3. A migration drift check (`makemigrations --check --dry-run`)
4. Migration application
5. API artifact export, with a diff check that fails if generated artifacts are
   stale
6. The full pytest suite

---

## API Artifacts

OpenAPI is the single source of truth for shareable API artifacts. Regenerate
them with:

```bash
cd backend
docker compose run --rm api python manage.py export_api_artifacts
```

This writes:

- `backend/docs/generated/openapi.json`
- `backend/docs/generated/ShieldTB.postman_collection.json`
- `backend/docs/generated/ShieldTB.local.postman_environment.json`

The Postman collection is intended for local development against
`http://localhost:8000`. Import and sharing guidance is in
[`docs/api-sharing.md`](docs/api-sharing.md). CI fails if these artifacts drift
from the committed schema.

---

## Project Structure

```
.
├── backend/
│   ├── apps/                  Domain apps (accounts, facilities, patients,
│   │                          clinical, risk, households, tasks,
│   │                          notifications, analytics, audit, core)
│   ├── config/                Settings, URL routing, API router, ASGI/WSGI
│   ├── docs/generated/        Generated OpenAPI and Postman artifacts
│   ├── docker-compose.yml     Local API and PostgreSQL services
│   ├── Dockerfile
│   └── pyproject.toml         Dependencies, Ruff, and pytest configuration
├── docs/
│   ├── adr/                   Architecture Decision Records
│   ├── architecture.md        Architecture narrative and build order
│   ├── security.md            JWT, claims, and logging policy
│   └── api-sharing.md         API artifact import and sharing guide
└── .github/workflows/         Continuous integration
```

---

## Delivery History

The backend was built in incremental milestones, each adding a vertical slice of
the TB care cascade:

1. **Foundation** — Django modular monolith scaffold, PostgreSQL-ready
   configuration, Docker Compose environment, and initial domain boundaries.
2. **Authentication** — secure JWT login, refresh, logout, and current-user
   endpoints; HttpOnly cookies; rotating refresh tokens; database-backed
   access-token revocation; role-based permissions; and CI.
3. **Patient registry and clinical intake** — facility-scoped patient registry
   with consent attribution, clinical encounter and intake APIs, automatic risk
   assessment creation, and OpenAPI/Postman artifact generation.
4. **Household contact tracing and workflow** — household tracing API, contact
   registration and screening-status updates, CHW assignment, automatic
   screening task creation, and workflow task assignment.
5. **Notifications** — a notification provider abstraction, in-app notification
   records for workflow-task assignment, and a read-only notifications API.
6. **Analytics** — live facility summary endpoints, daily facility metric
   snapshots, and an admin/analyst refresh path.
