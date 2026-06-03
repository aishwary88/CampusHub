# Implementation Plan: Authentication & User System

## Overview

Implements the complete Sprint 1 authentication stack for CampusHub: upgraded PostgreSQL-backed
User model with Alembic migrations, bcrypt password hashing, JWT issuance/verification,
email-domain role assignment, protected `/api/auth/me` endpoint, and a React frontend with
guarded routes and improved auth pages. The implementation follows the layered architecture in
the design document and must not break any existing route registrations.

---

## Tasks

- [x] 1. Upgrade User model and Pydantic schemas
  - [x] 1.1 Rewrite `app/models/user.py` with the full production schema
    - Add `UserRole` string enum (`STUDENT`, `FACULTY`, `ADMIN`)
    - Replace `full_name`/`hashed_password`/`is_active`/`otp_code` columns with
      `name`, `password_hash`, `role`, `branch`, `year`, `profile_photo`, `bio`, `campus_score`
    - Set `created_at` with `server_default=func.now()`, `updated_at` with `onupdate=func.now()`
    - Keep existing ORM relationships (`posts`, `notifications`, `clubs`, `events`)
    - _Requirements: 1.1, 1.2_

  - [x] 1.2 Rewrite `app/schemas/user.py` to match new model and design spec
    - `UserCreate`: fields `name` (optional str), `email` (EmailStr), `password` (`Field(min_length=8)`); remove `role`
    - `UserRead`: add `name`, `role`, `branch`, `year`, `profile_photo`, `bio`, `campus_score`, `created_at`, `updated_at`; remove `full_name`, `is_active`
    - Keep `Token`, `LoginRequest`; remove `OTPVerify`
    - _Requirements: 3.1, 3.3_

  - [ ]* 1.3 Write property test for short-password validation (Property 3)
    - **Property 3: Short passwords are always rejected**
    - Use `hypothesis` `text(max_size=7)` to confirm `UserCreate` raises `ValidationError` for passwords < 8 chars
    - Use `hypothesis` `text(min_size=8)` to confirm passwords ≥ 8 chars pass length validation
    - Place test in `backend/tests/test_auth_service.py`
    - **Validates: Requirements 3.3**

- [ ] 2. Harden password utilities and add property tests
  - [ ]* 2.1 Write property tests for `app/auth/password.py` (Properties 4, 5, 6, 7)
    - Create `backend/tests/test_password.py`; import `hash_password`, `verify_password`
    - **Property 4: Stored credential is never plaintext** — `hash_password(p) != p` for any `p`
    - **Property 5: Password hash verify round-trip** — `verify_password(p, hash_password(p)) == True`
    - **Property 6: Cross-password verification returns False** — `verify_password(p1, hash_password(p2)) == False` when `p1 != p2`
    - **Property 7: Bcrypt salt uniqueness** — two calls to `hash_password(p)` produce different hashes
    - Use `hypothesis` strategies `text(min_size=1)` for passwords
    - **Validates: Requirements 3.4, 4.1, 4.2, 4.3, 4.4**

- [x] 3. Upgrade JWT handler
  - [x] 3.1 Add `verify_token` to `app/auth/jwt_handler.py`
    - Import `JWTError`, `ExpiredSignatureError` from `jose`
    - Implement `verify_token(token: str) -> dict` that calls `decode_access_token`; on any
      `JWTError` or `None` result raises `HTTPException(status_code=401, detail="Could not validate credentials")`
    - Ensure `create_access_token` embeds `sub`, `id`, `role`, `exp` claims
    - Confirm expiry is set to 7 days from issuance
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ]* 3.2 Write property tests for `app/auth/jwt_handler.py` (Properties 8, 9, 10)
    - Create `backend/tests/test_jwt_handler.py`
    - **Property 8: Token always contains required claims** — decoded payload has `sub`, `id`, `role`, `exp` for any valid `(email, id, role)` triple
    - **Property 9: JWT encode–decode round-trip** — `decode_access_token(create_access_token(p))` returns payload with equivalent `sub`, `id`, `role`
    - **Property 10: Invalid tokens always raise 401** — tampered/expired tokens cause `verify_token` to raise `HTTPException` with `status_code == 401`
    - Use `hypothesis` composite strategies to generate token payloads and tampered token strings
    - **Validates: Requirements 5.2, 5.3, 5.4, 5.6**

- [x] 4. Implement email-domain role assignment in Auth Service
  - [x] 4.1 Rewrite `app/services/auth_service.py` with domain-based role logic
    - Add `ALLOWED_DOMAINS` dict: `{"mitsgwl.ac.in": UserRole.STUDENT, "mitsgwalior.in": UserRole.FACULTY}`
    - Implement `resolve_role(email: str) -> UserRole` — splits at `@`, lowercases domain, looks up `ALLOWED_DOMAINS`; raises `ValueError("Email domain not allowed")` for unknown domains
    - Update `create_user` to accept `name` instead of `full_name`; call `resolve_role` internally; catch `ValueError` and re-raise as `HTTPException(422)`; use `password_hash` column
    - Update `authenticate_user` to accept unverified check (returns `None` but caller will check `is_verified`)
    - Remove `generate_otp` and `set_otp_for_user` (out of scope for this sprint)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.4_

  - [ ]* 4.2 Write property tests for `resolve_role` (Properties 1, 2)
    - Add to `backend/tests/test_auth_service.py`
    - **Property 1: Non-MITS domain registration is always rejected** — generate arbitrary domains that are not `mitsgwl.ac.in` or `mitsgwalior.in`; confirm `resolve_role` raises `ValueError`
    - **Property 2: Domain comparison is case-insensitive** — generate case variations of `mitsgwl.ac.in` and `mitsgwalior.in`; confirm correct role returned
    - Use `hypothesis` strategies with `sampled_from` and string case transformations
    - **Validates: Requirements 2.3, 2.4**

- [x] 5. Upgrade Auth Router with registration, login, and /me endpoints
  - [x] 5.1 Rewrite `app/routers/auth.py` with updated endpoint logic
    - `POST /api/auth/register`: call `auth_service.create_user(db, name, email, password)`;
      return HTTP 201 with `UserRead`; on duplicate email raise HTTP 409 `"Email already registered"`;
      on domain error propagate HTTP 422; remove OTP generation
    - `POST /api/auth/login`: call `auth_service.authenticate_user`; if `None` raise HTTP 401
      `"Invalid credentials"`; if user exists but `is_verified == False` raise HTTP 403
      `"Email not verified"`; call `jwt_utils.create_access_token` with `sub`, `id`, `role` claims; return `Token`
    - `GET /api/auth/me`: add new endpoint protected by `Depends(get_current_user)` (from `app/auth/jwt.py`);
      return HTTP 200 with `UserRead` for the current user
    - Import `status` from `fastapi` for semantic status codes
    - _Requirements: 3.1, 3.2, 3.3, 6.1, 6.2, 6.3, 6.4, 7.1, 7.2, 7.3_

  - [x] 5.2 Update `app/auth/jwt.py` `get_current_user` to use `verify_token`
    - Replace the inline `jwt.decode` + `JWTError` try/except with a call to `jwt_handler.verify_token`
    - Ensure `get_current_user` still queries the DB for the user and raises `credentials_exception` if not found
    - _Requirements: 7.2, 7.3_

- [x] 6. Checkpoint — verify backend unit tests pass
  - [x] 6.1 Create `backend/tests/__init__.py` and `backend/tests/conftest.py`
    - Add pytest fixtures: in-memory SQLite `db` session for unit tests; test `client` using FastAPI `TestClient`; `test_user` factory fixture
    - Add `hypothesis` settings profile (`max_examples=100`)
    - _Requirements: 3.1, 4.2, 5.3_

  - [x] 6.2 Write example-based router tests in `backend/tests/test_auth_router.py`
    - Test happy-path register → 201 + UserRead (no `password_hash` in response)
    - Test duplicate email → 409
    - Test non-MITS domain → 422
    - Test password < 8 chars → 422
    - Test valid login → 200 + Token
    - Test unknown email login → 401
    - Test wrong password → 401
    - Test unverified user login → 403
    - Test `GET /api/auth/me` with valid token → 200
    - Test `GET /api/auth/me` without token → 401
    - Test `GET /api/auth/me` with invalid token → 401
    - Test STUDENT domain (`mitsgwl.ac.in`) assignment
    - Test FACULTY domain (`mitsgwalior.in`) assignment
    - _Requirements: 3.1, 3.2, 6.1, 6.2, 6.3, 6.4, 7.1, 7.2, 7.3_

  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Configure Alembic and generate initial PostgreSQL migration
  - [x] 7.1 Initialise Alembic at the project root
    - Run `alembic init alembic` in `c:\CampusHub\` to create `alembic.ini` and `alembic/env.py`
    - Edit `alembic.ini`: set `sqlalchemy.url = %(DATABASE_URL)s`
    - Edit `alembic/env.py`: load `.env` with `dotenv`; call `config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))`; import `Base` and all models before `target_metadata = Base.metadata`
    - Add `alembic` to `backend/requirements.txt`
    - _Requirements: 8.1, 8.2_

  - [x] 7.2 Generate and validate the initial migration
    - Run `alembic revision --autogenerate -m "initial_users_table"` to produce `alembic/versions/0001_initial_users_table.py`
    - Verify the generated migration creates the `users` table with all columns from the design (including `password_hash`, `campus_score`, `branch`, `year`, `profile_photo`, `bio`)
    - Ensure old columns (`full_name`, `hashed_password`, `is_active`, `otp_code`) are absent from the migration
    - _Requirements: 1.3, 8.3_

  - [x] 7.3 Remove `Base.metadata.create_all` startup auto-create from `app/main.py`
    - Delete the `startup_event` function and its `@app.on_event("startup")` decorator
    - Remove the SQLite fallback from `app/database/database.py`; set the default `DATABASE_URL` to raise a clear `RuntimeError` if the env var is missing
    - _Requirements: 8.1, 8.2_

- [x] 8. Update TypeScript types and authService
  - [x] 8.1 Update `src/types/index.d.ts` with production-aligned types
    - Replace the existing `User` interface with fields matching `UserRead`: `id`, `name`, `email`, `role` (`"STUDENT" | "FACULTY" | "ADMIN"`), `branch`, `year`, `profile_photo`, `bio`, `campus_score`, `is_verified`, `created_at`, `updated_at`
    - Add `RegisterPayload`, `LoginPayload`, and `Token` interfaces
    - _Requirements: 9.1, 10.1_

  - [x] 8.2 Update `src/services/authService.ts`
    - Type the `register`, `login`, and add `getMe` functions using the new interfaces
    - `getMe()`: `GET /api/auth/me` with `Authorization: Bearer <token>` header read from `localStorage`
    - Ensure `login` stores `access_token` in `localStorage` under the key `"access_token"`
    - Export functions individually and as default object
    - _Requirements: 10.2, 10.5_

- [x] 9. Upgrade Register and Login pages
  - [x] 9.1 Rewrite `src/pages/auth/Register.tsx`
    - Fields: `name` (text), `email` (email), `password` (password) — remove the role `<select>`
    - Add `error` state; on backend error set `error` to `err.response?.data?.detail ?? "Registration failed"`; render error in a visible `<div>` below the form
    - On success navigate to `/login` (not `/otp`)
    - Call `authService.register({ name, email, password })`
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [x] 9.2 Upgrade `src/pages/auth/Login.tsx`
    - Add `error` state; on failure set `error` to `err.response?.data?.detail ?? "Login failed"`; render in a visible `<div>`; clear error on each new submission
    - On success navigate to `/` (already does this; verify `authService.login` stores the token)
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 10. Create PrivateRoute and update AppRoutes
  - [x] 10.1 Create `src/routes/PrivateRoute.tsx`
    - Read `localStorage.getItem("access_token")`
    - If token present: render `<Outlet />`
    - If token absent: render `<Navigate to="/login" replace />`
    - _Requirements: 11.1, 11.2, 11.3_

  - [x] 10.2 Update `src/routes/AppRoutes.tsx` to use PrivateRoute
    - Import `PrivateRoute`
    - Wrap the Home route (and any other protected routes) inside `<Route element={<PrivateRoute />}>`
    - Move `/otp` route to a public (AuthLayout) section; keep `/login` and `/register` public
    - _Requirements: 11.4_

- [ ] 11. Frontend tests
  - [ ]* 11.1 Write Vitest unit tests for Register.tsx
    - Test: renders `name`, `email`, `password` fields and no role selector (req 9.1, 9.2)
    - Test: shows backend `detail` error on 422 without navigating (req 9.3)
    - Test: navigates to `/login` on success (req 9.4)
    - Create `frontend/src/__tests__/Register.test.tsx`
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

  - [ ]* 11.2 Write Vitest unit tests for Login.tsx
    - Test: renders `email` and `password` fields (req 10.1)
    - Test: calls `authService.login` with correct payload (req 10.5)
    - Test: shows error on 401 without navigating (req 10.4)
    - Test: navigates to `/` on success (req 10.3)
    - Create `frontend/src/__tests__/Login.test.tsx`
    - _Requirements: 10.1, 10.3, 10.4, 10.5_

  - [ ]* 11.3 Write property-style Vitest tests for authService and PrivateRoute (Properties 11, 12)
    - Create `frontend/src/__tests__/PrivateRoute.test.tsx`
    - **Property 11: Login response token is persisted to localStorage** — parameterize over token strings; confirm `authService.login` stores the exact token value under `"access_token"`
    - **Property 12: PrivateRoute renders children for any non-empty token** — for a set of varied non-empty token strings confirm `PrivateRoute` renders `<Outlet />` not redirect; for empty/missing token confirm redirect to `/login`
    - **Validates: Requirements 10.2, 11.1, 11.2**

- [x] 12. Final checkpoint — all tests pass
  - Ensure all backend pytest tests pass (`pytest backend/tests/`).
  - Ensure all frontend Vitest tests pass (`vitest --run` from `frontend/`).
  - Ask the user if any questions arise before closing the sprint.

---

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP.
- Each task references specific requirements for traceability.
- Property tests use `hypothesis` (backend) and parameterized Vitest tests (frontend).
- Alembic tasks (7.x) require a running PostgreSQL instance to run `upgrade head`; unit/property tests use SQLite in-memory.
- The `otp_code` column and OTP endpoints are retained in the DB migration for future sprints but OTP business logic is out of scope here.
- Do **not** remove existing ORM relationships on `User`; other routers (`clubs`, `events`, `posts`) depend on them.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["1.3", "2.1", "3.1", "4.1"] },
    { "id": 2, "tasks": ["3.2", "4.2", "5.1", "5.2", "8.1"] },
    { "id": 3, "tasks": ["6.1", "6.2", "7.1", "8.2"] },
    { "id": 4, "tasks": ["7.2", "7.3", "9.1", "9.2", "10.1"] },
    { "id": 5, "tasks": ["10.2", "11.1", "11.2"] },
    { "id": 6, "tasks": ["11.3"] }
  ]
}
```
