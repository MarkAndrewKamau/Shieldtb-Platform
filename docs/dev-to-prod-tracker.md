# Dev To Prod Tracker

This document tracks development-time choices that are acceptable for local
builds, pilots, or internal demos but should be reviewed before production.

Use it as a running checklist. Each item should either:

- be closed out by code/config changes, or
- be replaced by an ADR if the compromise becomes intentional long-term design.

## How to use this file

For each item, track:

- the current development behavior
- why it is acceptable right now
- what production should look like
- the trigger for changing it

## Current items

### 1. Mobile auth uses explicit token mode

- **Area:** mobile auth
- **Current dev behavior:** the mobile client explicitly sends
  `auth_mode: "token"` for login, signup, and refresh so the backend returns
  access and refresh tokens in the JSON response body.
- **Important clarification:** token values are **not hardcoded** in the app.
  What is hardcoded today is the auth mode choice and the secure-storage key
  names in [apps/mobile/src/stores/auth.ts](/home/markandrew/Tb-Solution/Shieldtb-Platform/apps/mobile/src/stores/auth.ts).
- **Why acceptable now:** native clients cannot use browser HttpOnly cookies in
  the same way as the web app; returning tokens is required for the mobile app
  to work.
- **Production target:** keep secure token delivery for native clients, but
  tighten the mobile auth story with:
  - stronger refresh-token misuse detection
  - optional device binding/session metadata
  - documented session revocation behavior across multiple devices
  - production review of secure-storage guarantees per platform
- **Trigger to revisit:** before public pilot rollout or before supporting
  multiple concurrent devices per user.

### 2. Mobile API base URL has a localhost fallback

- **Area:** mobile configuration
- **Current dev behavior:** the mobile app falls back to
  `http://127.0.0.1:8000` if `EXPO_PUBLIC_API_BASE_URL` is missing in
  [apps/mobile/src/lib/env.ts](/home/markandrew/Tb-Solution/Shieldtb-Platform/apps/mobile/src/lib/env.ts).
- **Why acceptable now:** it reduces setup friction for emulator/local
  development.
- **Production target:** require an explicit environment-specific API base URL
  at build/release time and fail fast if missing.
- **Trigger to revisit:** before staging or production mobile builds.

### 3. Public mobile signup requires raw facility ID

- **Area:** mobile signup / onboarding
- **Current dev behavior:** signup requires the numeric backend `facility` ID.
- **Why acceptable now:** it matches the current backend contract and unblocks
  end-to-end flow testing quickly.
- **Production target:** replace raw numeric facility ID entry with one of:
  - invite-based signup
  - facility code lookup
  - searchable facility picker
- **Trigger to revisit:** before any real CHW onboarding outside the dev team.

### 4. Public signup is open for non-admin accounts

- **Area:** backend auth / onboarding
- **Current dev behavior:** non-admin users can self-register through the public
  signup endpoint.
- **Why acceptable now:** it speeds up testing and mobile auth development.
- **Production target:** require invitation, approval, or pre-provisioned staff
  onboarding tied to facility administration.
- **Trigger to revisit:** before deployment for real clinical or operational
  users.

### 5. Broad development host/origin settings

- **Area:** backend environment configuration
- **Current dev behavior:** local development may include emulator/LAN hosts in
  `DJANGO_ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`.
- **Why acceptable now:** emulator and local-network testing need flexible host
  access.
- **Production target:** strictly scoped host and origin allowlists per
  environment.
- **Trigger to revisit:** before staging and production deployment.

### 6. Django dev server is used in Docker Compose

- **Area:** backend runtime
- **Current dev behavior:** Docker Compose runs `python manage.py runserver`.
- **Why acceptable now:** it is simple and fast for local iteration.
- **Production target:** use Gunicorn/ASGI process management, hardened static
  asset handling, and production-grade container/runtime settings.
- **Trigger to revisit:** before first deployed environment beyond local dev.

### 7. Access-token revocation uses PostgreSQL blocklist

- **Area:** auth infrastructure
- **Current dev behavior:** revoked access-token `jti` values are checked from a
  database-backed blocklist.
- **Why acceptable now:** it gives us immediate revocation without introducing
  Redis yet.
- **Production target:** move to Redis-backed revocation once traffic, service
  count, or latency warrants it.
- **Trigger to revisit:** see
  [0001-database-backed-access-token-blocklist.md](/home/markandrew/Tb-Solution/Shieldtb-Platform/docs/adr/0001-database-backed-access-token-blocklist.md).

### 8. Notifications are synchronous and in-app first

- **Area:** notifications
- **Current dev behavior:** notification creation/dispatch is synchronous and
  limited to the in-app path.
- **Why acceptable now:** it keeps Week 7 functionality inspectable and easy to
  verify.
- **Production target:** async dispatch, retries, provider adapters, and delivery
  monitoring.
- **Trigger to revisit:** before SMS/WhatsApp rollout or larger workflow volume.

### 9. Analytics are partly live and partly manually refreshed

- **Area:** analytics
- **Current dev behavior:** facility summaries are live; daily snapshots rely on
  explicit refresh commands/actions.
- **Why acceptable now:** it avoids background infrastructure while analytics
  needs are still small.
- **Production target:** scheduled refresh jobs with observability and failure
  alerting.
- **Trigger to revisit:** before production dashboards are relied on
  operationally.

### 10. Mobile auth/session state is single-profile only

- **Area:** mobile app session model
- **Current dev behavior:** the app stores one active user session locally with a
  simple refresh/retry flow.
- **Why acceptable now:** it is enough for the first CHW MVP.
- **Production target:** explicitly define session replacement, lost-device
  handling, sign-out-from-all-devices, and account-switch behavior.
- **Trigger to revisit:** before field deployment to shared or rotating devices.

## Closed items

Move items here once they have been addressed in code/config and no longer
represent a production-readiness gap.
