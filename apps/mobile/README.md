# ShieldTB Mobile

React Native mobile app for CHW and field workflows.

## Stack

- Expo
- React Native
- Expo Router
- TanStack Query
- Zustand
- React Hook Form
- Expo Secure Store

## Environment

Create `apps/mobile/.env` from `.env.example`.

```bash
EXPO_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

For a physical device, replace `127.0.0.1` with the LAN IP of the machine
running the Django API.

## Auth mode

The mobile app uses the backend's native-client auth path:

- `POST /api/v1/auth/login/` with `auth_mode: "token"`
- `POST /api/v1/auth/refresh/` with `auth_mode: "token"`

Tokens are stored in device secure storage, not in web cookies.
