# ADR 0002: PostgreSQL as the Primary Database

## Status

Accepted.

## Context

ShieldTB handles clinical workflow data, audit logs, facility-scoped access,
household tracing, analytics, and eventually geospatial hotspot mapping.

SQLite is useful for tiny prototypes, but it does not match the database
features or operational behavior this platform needs.

## Decision

Use PostgreSQL as the primary database for development, CI, staging, and
production.

Docker Compose runs PostgreSQL locally. GitHub Actions runs tests against a
PostgreSQL service. Django settings default to a local PostgreSQL URL if
`DATABASE_URL` is not provided.

## Why

- Production parity from the start.
- Strong transactional behavior for clinical intake and risk scoring.
- Better fit for audit and reporting workloads.
- Natural path to PostGIS for household tracing and hotspot mapping.
- Avoids subtle behavior differences between SQLite and PostgreSQL.

## Consequences

- Developers need PostgreSQL via Docker or a local service.
- Tests should keep using PostgreSQL in CI.
- Future geospatial work should add PostGIS rather than a separate spatial
  database.

## Revisit Triggers

This decision should only be revisited if the platform moves to a managed
health-data platform that supplies a PostgreSQL-compatible datastore or another
clinically compliant database with stronger operational guarantees.

