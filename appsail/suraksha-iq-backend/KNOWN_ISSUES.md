# Known Issues — SurakshaIQ Backend

## 1. Temporary Auth Bypass (DEV_SKIP_AUTH)
- **Location:** `app/api/deps.py` — `get_current_user()` function
- **What:** When `DEV_SKIP_AUTH=true` AND `environment=development` AND `debug=true`, JWT auth is bypassed and a mock officer dict is injected.
- **Action required:** **Remove or confirm `DEV_SKIP_AUTH=false` before any demo or deployment.** The flag defaults to `false` in `settings.py` and must only ever be set in a local `.env` file that is gitignored.
- **Owner:** Backend team
- **Priority:** High — must be resolved before production exposure.

## 2. Temporary Frontend Auth Bypass (VITE_DEV_SKIP_AUTH)
- **Location:** `client/src/contexts/AuthContext.tsx` — `refreshSession()` function
- **What:** When `VITE_DEV_SKIP_AUTH=true` (set in local `client/.env`, gitignored), the frontend route guard and session refresh are skipped. A mock `SYSTEM_ADMINISTRATOR` officer is injected into the auth context. Requests to protected endpoints still succeed because the backend also checks `DEV_SKIP_AUTH`.
- **Action required:** **Confirm `VITE_DEV_SKIP_AUTH=false` before any demo or deployment.** Must only be set in a local `.env` file that is gitignored.
- **Owner:** Frontend team
- **Priority:** High — must be resolved before production exposure.

## 3. VITE_API_URL Pointed at Localhost
- **Location:** `client/.env` (gitignored)
- **What:** `VITE_API_URL` is set to `http://localhost:8080/api/v1` for local development instead of the deployed Catalyst URL.
- **Action required:** **MUST be reverted to the deployed Catalyst URL before any deployment or shared demo.** The production URL is preserved as a comment in `client/.env` for easy restoration.
- **Owner:** Frontend team
- **Priority:** High — must be resolved before production exposure.

---

_Add new items above, do not delete resolved items._
