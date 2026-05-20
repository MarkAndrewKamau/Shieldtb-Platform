# ADR 0003: Synchronous In-App Notifications First

## Status

Accepted for Week 7.

## Context

ShieldTB now has workflow tasks and household tracing, which means assigned CHWs
need timely reminders. The long-term platform will likely deliver notifications
through Celery-backed background jobs and external providers such as SMS or
WhatsApp adapters.

At Week 7, the product needs notification records and a delivery abstraction,
but it does not yet need external provider dependencies or queue infrastructure.

## Decision

Start with:

- a first-class `Notification` model
- synchronous dispatch inside the web process
- an in-app provider for workflow assignment reminders
- a provider abstraction so later channels can plug in without rewriting the
  calling code

The first hook is workflow-task assignment notification for CHWs.

## Why This Is Acceptable Now

- It creates real delivery records and API-visible state immediately.
- It keeps notification behavior testable without external services.
- It avoids introducing Celery and Redis before scheduled reminder workloads
  exist.
- It gives the team a stable integration surface for future SMS and WhatsApp
  adapters.

## Consequences

Positive:

- Week 7 gets usable reminder infrastructure quickly.
- Notification records are inspectable and auditable.
- API consumers can already list notification state.

Tradeoffs:

- Dispatch happens during request/response for now.
- Scheduled reminders are stored but not yet processed asynchronously.
- External delivery reliability and retries are not yet implemented.

## Revisit Triggers

Move to async worker-backed delivery when any of these become true:

- We introduce scheduled reminders beyond immediate assignment notices.
- External providers like SMS or WhatsApp are added.
- Request latency becomes sensitive to delivery side effects.
- Notification retries, rate limits, or backoff become operational needs.

## Future Design

Keep the application-facing notification service stable while moving dispatch to:

- Celery tasks
- Redis-backed queues
- provider-specific adapters with retry policy
