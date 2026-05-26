# ShieldTB Security Notes

## JWT Policy

ShieldTB uses short-lived access tokens and rotating refresh tokens.

- Access tokens expire after 15 minutes.
- Refresh tokens expire after 7 days.
- Refresh tokens rotate on use and the previous refresh token is blacklisted.
- Access tokens include a `jti`; logout stores the current `jti` in a blocklist.
- Tokens are delivered through HttpOnly cookies for browser clients.
- Native/mobile clients may explicitly request `auth_mode: "token"` and store
  returned access/refresh tokens in secure device storage.
- Browser cookie authentication enforces CSRF checks for unsafe requests.
- API clients may still use `Authorization: Bearer <token>`.
- Raw access and refresh tokens are not returned from browser-mode login
  responses.

See `docs/adr/0001-database-backed-access-token-blocklist.md` for the MVP
decision to use database-backed access-token revocation first, with clear
triggers for moving the same design to Redis later.

## Algorithm Controls

The JWT algorithm is configured server-side with `JWT_ALGORITHM`.
`alg: none` is rejected by configuration and covered by tests. Do not use token
headers to dynamically decide verification behavior.

For HS256, use a high-entropy `JWT_SIGNING_KEY` with at least 32 random bytes.
Generate one with:

```bash
openssl rand -base64 32
```

Use different signing keys in development, staging, and production.

## Claims

Keep claims minimal:

- `sub`/user id
- `role`
- `facility_id`
- `iss`
- `aud`
- `iat`
- `exp`
- `jti`

Do not put clinical data, HIV status, pregnancy status, household address,
permissions lists, passwords, or other sensitive PII in JWT payloads.

## Logging

Audit events store action, actor, resource, IP address, user agent, and redacted
metadata. Raw `Authorization`, cookie, access-token, refresh-token, and password
values must never be stored in logs or audit metadata.
