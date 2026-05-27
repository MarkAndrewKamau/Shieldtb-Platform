# Frontend Roadmap

This document tracks frontend delivery the same way we tracked the backend:

- what is already done
- what remains
- the recommended build order

ShieldTB is now officially **mobile-first, web-next**:

- **mobile app first** for CHWs and field workflows
- **web app next** for clinicians, facility staff, analysts, and admins

The backend API remains the shared source of truth for both clients.

## Current frontend state

### Completed foundation

The following work is already done:

1. **Frontend workspace shape**
   - `apps/mobile`
   - `packages/types`
   - `packages/api-client`

2. **Shared TypeScript packages**
   - shared auth/user/task/household types
   - shared API client for backend endpoints already in use

3. **Mobile runtime and navigation**
   - Expo + React Native
   - Expo Router
   - TanStack Query
   - Zustand auth/session store
   - React Hook Form

4. **Native mobile auth support**
   - backend supports `auth_mode: "token"` for native clients
   - mobile app stores session state in Expo Secure Store
   - login flow works end to end
   - signup flow works end to end for non-admin roles
   - refresh/logout flow is wired into the auth store

5. **First CHW mobile screens**
   - sign in
   - sign up
   - task list
   - task detail
   - household detail
   - household contact status updates

6. **Local development path**
   - emulator setup works
   - mobile app can reach backend through `10.0.2.2`
   - backend/mobile local env split is understood and documented

## What is not done yet

The frontend is still missing several important layers:

- offline-first storage and sync queue
- mobile notifications/inbox UI
- patient summary view
- analytics/dashboard frontend
- clinician/admin web app
- frontend test coverage
- release/build pipeline for mobile

## Phase plan

## Phase 9 - Mobile foundation

**Status:** completed

Delivered:

- workspace structure
- shared API/types packages
- mobile auth
- CHW task flow starter screens
- household detail and contact updates

## Phase 10 - Mobile onboarding and session polish

**Status:** completed

Goal: make the app usable for first-time staff without backend-ID guesswork.

Delivered:

1. **Better signup/onboarding**
   - replace raw `facility ID` input
   - support facility code or facility search
   - optionally move toward invite-based signup

2. **Session polish**
   - clearer login/signup errors
   - sign-out confirmation
   - session expiry/re-auth messaging
   - account bootstrap/loading polish

3. **Profile basics**
   - current user summary
   - role/facility display
   - simple account screen

## Phase 11 - CHW workflow completion

**Status:** planned

Goal: complete the first practical field workflow loop.

Build:

1. **Patient summary screen**
   - index patient identity/context
   - linked household context
   - recent risk tier and clinical summary where available

2. **Task workflow polish**
   - filters by status
   - due-state presentation
   - better task metadata rendering

3. **Household workflow polish**
   - add/view richer contact details
   - clearer screening-state progression
   - household map/address presentation improvements

## Phase 12 - Mobile notifications and in-app awareness

**Status:** planned

Goal: expose the backend notification model inside the mobile client.

Build:

1. **Notification inbox**
   - notification list
   - notification detail
   - unread/read state if added backend-side

2. **Workflow-linked navigation**
   - open task from notification
   - open household from notification

3. **Reminder UX**
   - surface missed follow-up and assignment reminders clearly

## Phase 13 - Offline-first mobile

**Status:** planned

Goal: make CHW workflows resilient in low-connectivity settings.

Build:

1. **Local cache strategy**
   - define what must be available offline
   - tasks
   - assigned households
   - contact forms/drafts

2. **Mutation queue**
   - queue contact status updates
   - queue task status updates
   - retry on reconnect

3. **Sync UX**
   - last synced indicator
   - pending changes count
   - conflict/failure states

## Phase 14 - Frontend testing and quality baseline

**Status:** planned

Goal: avoid shipping fragile mobile flows as the surface area grows.

Build:

1. **Unit tests**
   - auth store
   - API client behavior
   - form helpers

2. **Component/screen tests**
   - login/signup flows
   - task list rendering
   - household contact update behavior

3. **CI frontend checks**
   - typecheck
   - lint
   - tests

## Phase 15 - Web foundation

**Status:** planned

Goal: begin the web app for clinicians and facility/admin users.

Recommended stack:

- React
- TypeScript
- Vite
- React Router
- TanStack Query
- Zustand
- React Hook Form
- Tailwind CSS
- shadcn/ui

Build:

1. **Workspace scaffold**
   - `apps/web`
   - shared API client usage
   - shared auth/domain types

2. **Web auth**
   - browser cookie auth
   - login screen
   - protected routes

3. **Operational shell**
   - app layout
   - sidebar/topbar
   - role-aware navigation

## Phase 16 - Web operational dashboards

**Status:** planned

Goal: expose the backend’s operational/admin value on desktop.

Build:

1. **Facility dashboard**
   - facility summaries
   - daily metrics
   - open tasks
   - contact screening counts

2. **Patient and household views**
   - patient registry browsing
   - intake/risk visibility
   - household tracing views

3. **Care-team workflows**
   - task assignment
   - follow-up monitoring
   - notification visibility

## Phase 17 - Release hardening

**Status:** planned

Goal: prepare the frontend side for real pilot use.

Build:

1. **Mobile release pipeline**
   - production env handling
   - build profiles
   - signing/release steps

2. **Frontend observability**
   - crash reporting
   - client-side logging policy
   - API error instrumentation

3. **Security review**
   - mobile session model review
   - secure storage review
   - environment/config hardening

## Recommended next move

The best next step is:

1. **Phase 10**
2. then **Phase 11**
3. then **Phase 12**
4. then **Phase 13**
5. only after that begin the first **web foundation**

That order keeps us aligned with the actual audience:

- CHWs need a usable field app first
- clinicians/admins benefit once the operational data flow is stronger

## Relationship to other docs

- production caveats and deferred hardening live in
  [docs/dev-to-prod-tracker.md](/home/markandrew/Tb-Solution/Shieldtb-Platform/docs/dev-to-prod-tracker.md)
- backend architecture lives in
  [docs/architecture.md](/home/markandrew/Tb-Solution/Shieldtb-Platform/docs/architecture.md)
