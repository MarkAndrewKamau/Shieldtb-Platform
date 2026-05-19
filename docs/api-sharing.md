# API Sharing

ShieldTB treats OpenAPI as the source of truth for API-sharing artifacts.
Postman files are generated from that schema so the collection stays aligned
with the backend as we add modules.

## Generate Artifacts

```bash
cd backend
docker compose run --rm api python manage.py export_api_artifacts
```

This writes:

- `backend/docs/generated/openapi.json`
- `backend/docs/generated/ShieldTB.postman_collection.json`
- `backend/docs/generated/ShieldTB.local.postman_environment.json`

## Import Into Postman

1. Import `ShieldTB.postman_collection.json`.
2. Import `ShieldTB.local.postman_environment.json`.
3. Select the `ShieldTB Local` environment.
4. Switch Postman from Cloud Agent to Desktop Agent for localhost requests.
5. Set `baseUrl`, `username`, `password`, and `email` for your local user.

## Suggested First Run

1. `Health check`
2. `Create facility`
3. `Sign up` or `Create user`
4. `Log in`
5. `Create patient`
6. `Create structured intake`
7. `Create household trace`

The generated collection captures IDs into environment variables as you go:

- `facilityId`
- `userId`
- `patientId`
- `encounterId`
- `householdId`
- `contactId`

Auth flows also capture:

- `accessToken`
- `refreshToken`

`Log out` clears the token variables from the environment.

## Team Workflow

- Regenerate artifacts whenever API routes, serializers, or auth behavior change.
- Commit the generated files alongside the backend change.
- CI checks that generated artifacts remain in sync with the codebase.
