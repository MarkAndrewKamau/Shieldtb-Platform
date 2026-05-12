# ADR 0001: Database-Backed Access Token Blocklist First

## Status

Accepted for MVP.

## Context

ShieldTB needs JWT logout and token-compromise handling from the beginning.
Access tokens are short-lived, but a stolen access token should still be
revocable before its 15-minute expiry when a user logs out or an account is
suspected to be compromised.

The ideal high-throughput implementation is a Redis-backed blocklist keyed by
JWT `jti`, with each revoked token expiring automatically at the token's
remaining TTL.

For the MVP, Redis is not yet otherwise required. Introducing it now would add
another operational dependency before background jobs, reminders, and workflow
queues exist.

## Decision

Use a database-backed `AccessTokenBlocklist` model for MVP access-token
revocation.

The implementation stores:

- `jti`
- `expires_at`
- `revoked_by`
- `reason`
- `created_at`

Authentication checks the current access token's `jti` against this blocklist.
Refresh tokens use SimpleJWT's built-in blacklist tables with refresh-token
rotation enabled.

## Why This Is Acceptable Now

- Access tokens expire after 15 minutes.
- Logout and compromise handling work immediately.
- The implementation is simple, inspectable, and easy to audit.
- Database volume during MVP/pilot usage should be low.
- The app already depends on PostgreSQL.

## Consequences

Positive:

- No Redis operational dependency during Week 2.
- Revocation state is visible in Django admin and queryable during debugging.
- The security behavior is testable immediately.

Tradeoffs:

- Every authenticated request performs a database existence check.
- Expired blocklist rows need periodic cleanup.
- This will not be the right design for high request volume or many services.

## Revisit Triggers

Move access-token revocation to Redis when any of these become true:

- API traffic makes the blocklist DB lookup measurable in latency or load.
- Redis is introduced for Celery, reminders, workflow queues, or caching.
- The platform has multiple backend services that need shared revocation checks.
- We need automatic key expiry instead of scheduled database cleanup.
- We start performance/load testing for a facility or county-level pilot.

## Future Design

Use Redis keys like:

```text
auth:blocklist:access:<jti> = 1
```

Set the expiry to the access token's remaining lifetime:

```text
EX = token_exp - current_time
```

Keep the application-facing interface stable so the auth layer can switch from
database lookup to Redis lookup without changing endpoint behavior.

