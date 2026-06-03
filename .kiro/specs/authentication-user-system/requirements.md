# Requirements Document

## Introduction

Sprint 1 of CampusHub — a campus social platform for MITS Gwalior students — delivers the complete
Authentication & User System. This feature covers user registration with institutional email-domain
validation, bcrypt password hashing, JWT issuance and verification, protected-route enforcement on
the frontend, and the upgrade of the existing SQLite-backed skeleton to PostgreSQL with Alembic
migrations.

The happy path is: **Register → (email domain auto-assigns role) → Login → Receive JWT →
Access protected Home page.**

---

## Glossary

- **Auth_Service**: The backend Python module (`app/services/auth_service.py`) responsible for
  user creation, credential verification, and email-domain role assignment logic.
- **JWT_Handler**: The backend Python module (`app/auth/jwt_handler.py`) responsible for
  creating and verifying JSON Web Tokens using `python-jose[cryptography]`.
- **Password_Hasher**: The backend utility (`app/auth/password.py`) that wraps
  `passlib[bcrypt]` for hashing and verifying passwords.
- **Auth_Router**: The FastAPI router (`app/routers/auth.py`) that exposes
  `/api/auth/register`, `/api/auth/login`, and `/api/auth/me`.
- **User_Model**: The SQLAlchemy ORM model (`app/models/user.py`) representing the `users`
  table in PostgreSQL.
- **Alembic**: The database migration tool used to version-control schema changes.
- **PrivateRoute**: The React component (`src/routes/PrivateRoute.tsx`) that guards pages
  requiring authentication on the frontend.
- **Auth_Store**: The browser `localStorage` key `access_token` used to persist the JWT on
  the client.
- **EmailDomainValidator**: The logic inside Auth_Service that maps email domains to roles.
- **Role**: An enumerated string value assigned to every user: `STUDENT`, `FACULTY`, or
  `ADMIN`.

---

## Requirements

### Requirement 1: User Model Schema

**User Story:** As a developer, I want a fully-specified User database model, so that all
authentication and profile data is stored consistently in PostgreSQL.

#### Acceptance Criteria

1. THE User_Model SHALL define the following columns: `id` (integer primary key), `name`
   (string, nullable), `email` (string, unique, non-nullable), `password_hash` (string,
   non-nullable), `role` (string enum: `STUDENT`, `FACULTY`, `ADMIN`, non-nullable),
   `branch` (string, nullable), `year` (integer, nullable), `profile_photo` (string,
   nullable), `bio` (text, nullable), `campus_score` (integer, default 0), `is_verified`
   (boolean, default false), `created_at` (datetime, auto-set on insert), `updated_at`
   (datetime, auto-updated on change).
2. THE User_Model SHALL use `password_hash` as the column name for the hashed credential,
   replacing the existing `hashed_password` column name.
3. THE Alembic SHALL generate an initial migration that creates the `users` table with the
   schema defined in Acceptance Criterion 1.
4. WHEN the PostgreSQL `DATABASE_URL` environment variable is set, THE Alembic migration
   SHALL apply to PostgreSQL without error.

---

### Requirement 2: Email Domain–Based Role Assignment

**User Story:** As a registering user, I want my institutional role to be assigned
automatically from my email address, so that I do not need to manually select a role during
registration.

#### Acceptance Criteria

1. WHEN a registration request contains an email whose domain is `mitsgwl.ac.in`, THE
   Auth_Service SHALL assign the role `STUDENT` to the new user.
2. WHEN a registration request contains an email whose domain is `mitsgwalior.in`, THE
   Auth_Service SHALL assign the role `FACULTY` to the new user.
3. WHEN a registration request contains an email whose domain is neither `mitsgwl.ac.in` nor
   `mitsgwalior.in`, THE Auth_Router SHALL return HTTP 422 with a descriptive error message
   and SHALL NOT create a user record.
4. THE Auth_Service SHALL determine the domain by splitting the email address at the `@`
   character and comparing the right-hand part (case-insensitively) against the allowed
   domains.

---

### Requirement 3: User Registration Endpoint

**User Story:** As a new user, I want to register with my name, email, and password, so that
I can create a CampusHub account.

#### Acceptance Criteria

1. WHEN a `POST /api/auth/register` request contains a valid email and a non-empty password,
   THE Auth_Router SHALL create a new user record via Auth_Service and return HTTP 201 with
   the `UserRead` schema (excluding `password_hash`).
2. WHEN a `POST /api/auth/register` request contains an email that already exists in the
   database, THE Auth_Router SHALL return HTTP 409 with the message
   `"Email already registered"` and SHALL NOT create a duplicate user record.
3. WHEN a `POST /api/auth/register` request contains a password shorter than 8 characters,
   THE Auth_Router SHALL return HTTP 422 with a descriptive validation error and SHALL NOT
   create a user record.
4. THE Auth_Service SHALL call Password_Hasher to hash the provided password before
   persisting the user record; THE Auth_Service SHALL NOT store plaintext passwords.

---

### Requirement 4: Password Hashing

**User Story:** As a security-conscious developer, I want all passwords to be hashed before
storage, so that user credentials are never exposed in plaintext.

#### Acceptance Criteria

1. THE Password_Hasher SHALL hash passwords using the bcrypt algorithm via
   `passlib[bcrypt]`.
2. WHEN a plaintext password is hashed and the resulting hash is then verified against the
   same plaintext, THE Password_Hasher SHALL return `True`.
3. WHEN a plaintext password is verified against a hash produced from a different password,
   THE Password_Hasher SHALL return `False`.
4. THE Password_Hasher SHALL produce a different hash output for each call even when the
   same plaintext password is provided (bcrypt salt uniqueness).

---

### Requirement 5: JWT Creation and Verification

**User Story:** As an authenticated user, I want to receive a signed JWT on login, so that I
can access protected API endpoints without re-sending my password on every request.

#### Acceptance Criteria

1. THE JWT_Handler SHALL create access tokens signed with HMAC-SHA256 (`HS256`) using the
   `SECRET_KEY` environment variable.
2. THE JWT_Handler SHALL embed the following claims in every token: `sub` (user email),
   `id` (user integer id), `role` (user role string), `exp` (expiry timestamp).
3. WHEN a valid, unexpired token is passed to `verify_token`, THE JWT_Handler SHALL return
   the decoded payload dictionary.
4. WHEN an expired or tampered token is passed to `verify_token`, THE JWT_Handler SHALL
   raise an `HTTPException` with status 401.
5. THE JWT_Handler SHALL set the token expiry to 7 days from the time of issuance.
6. FOR ALL valid token payloads `p`, encoding then decoding with the same secret SHALL
   produce an equivalent payload (round-trip property).

---

### Requirement 6: Login Endpoint

**User Story:** As a registered user, I want to log in with my email and password, so that I
receive a JWT to authenticate future requests.

#### Acceptance Criteria

1. WHEN a `POST /api/auth/login` request contains a valid email and correct password, THE
   Auth_Router SHALL return HTTP 200 with a JSON body containing `access_token` (string) and
   `token_type` set to `"bearer"`.
2. WHEN a `POST /api/auth/login` request contains an email that does not exist in the
   database, THE Auth_Router SHALL return HTTP 401 with the message
   `"Invalid credentials"`.
3. WHEN a `POST /api/auth/login` request contains a valid email but an incorrect password,
   THE Auth_Router SHALL return HTTP 401 with the message `"Invalid credentials"`.
4. WHEN a `POST /api/auth/login` request is received for an unverified user account, THE
   Auth_Router SHALL return HTTP 403 with the message `"Email not verified"`.

---

### Requirement 7: Authenticated User Endpoint

**User Story:** As a logged-in user, I want to fetch my own profile via a protected endpoint,
so that the frontend can display my account information.

#### Acceptance Criteria

1. WHEN a `GET /api/auth/me` request includes a valid Bearer token in the `Authorization`
   header, THE Auth_Router SHALL return HTTP 200 with the `UserRead` schema for the
   requesting user.
2. WHEN a `GET /api/auth/me` request is made without a Bearer token, THE Auth_Router SHALL
   return HTTP 401.
3. WHEN a `GET /api/auth/me` request is made with an expired or invalid token, THE
   Auth_Router SHALL return HTTP 401.

---

### Requirement 8: Database Migration to PostgreSQL

**User Story:** As a developer, I want the backend to use PostgreSQL with Alembic migrations
instead of the SQLite fallback, so that the database schema is version-controlled and
production-ready.

#### Acceptance Criteria

1. WHEN the `DATABASE_URL` environment variable points to a PostgreSQL instance, THE
   database connection module SHALL connect to PostgreSQL and SHALL NOT fall back to SQLite.
2. THE Alembic configuration SHALL target the same `DATABASE_URL` used by the FastAPI
   application.
3. WHEN `alembic upgrade head` is run against an empty PostgreSQL database, Alembic SHALL
   create all required tables without error.
4. IF `alembic upgrade head` is run against a database that already has the latest migration
   applied, THEN Alembic SHALL complete without error and SHALL NOT duplicate tables.

---

### Requirement 9: Frontend Register Page Upgrade

**User Story:** As a prospective MITS student or faculty member, I want a registration form
that collects my name, email, and password and submits them to the backend, so that I can
create my CampusHub account.

#### Acceptance Criteria

1. THE Register page SHALL display input fields for `name`, `email`, and `password`.
2. THE Register page SHALL NOT display a manual role selector, because role is derived
   automatically from the email domain.
3. WHEN the registration form is submitted with a non-MITS email address, THE Register page
   SHALL display the error message returned by the backend without navigating away.
4. WHEN the registration form is submitted successfully, THE Register page SHALL navigate
   the user to the Login page.
5. THE Register page SHALL call the `POST /api/auth/register` endpoint via Auth_Service.

---

### Requirement 10: Frontend Login Page Upgrade

**User Story:** As a registered user, I want a login form that submits my credentials and
stores the returned JWT, so that I can access protected pages.

#### Acceptance Criteria

1. THE Login page SHALL display input fields for `email` and `password`.
2. WHEN login succeeds, THE Login page SHALL store the `access_token` value returned by the
   backend into the Auth_Store (`localStorage`).
3. WHEN login succeeds, THE Login page SHALL navigate the user to the Home page (`/`).
4. WHEN login fails, THE Login page SHALL display a user-readable error message without
   navigating away.
5. THE Login page SHALL call the `POST /api/auth/login` endpoint via Auth_Service.

---

### Requirement 11: Protected Route (PrivateRoute Component)

**User Story:** As a developer, I want a PrivateRoute component that guards authenticated
pages, so that unauthenticated users are automatically redirected to the Login page.

#### Acceptance Criteria

1. WHEN a user navigates to a route wrapped by PrivateRoute and a valid JWT exists in the
   Auth_Store, THE PrivateRoute SHALL render the requested page.
2. WHEN a user navigates to a route wrapped by PrivateRoute and no JWT exists in the
   Auth_Store, THE PrivateRoute SHALL redirect the user to `/login`.
3. THE PrivateRoute SHALL check for the presence of the `access_token` key in
   `localStorage` to determine authentication state.
4. THE AppRoutes component SHALL wrap the Home page (and any other protected pages) with
   PrivateRoute.
