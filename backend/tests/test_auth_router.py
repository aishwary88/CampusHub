"""
Example-based tests for the Auth Router.

Covers:
- POST /api/auth/register  (req 3.1, 3.2, 3.3, 2.1, 2.2, 2.3)
- POST /api/auth/login     (req 6.1, 6.2, 6.3, 6.4)
- GET  /api/auth/me        (req 7.1, 7.2, 7.3)
"""

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

STUDENT_EMAIL = "alice@mitsgwl.ac.in"
FACULTY_EMAIL = "bob@mitsgwalior.in"
VALID_PASSWORD = "securepassword123"


def _register(client, email=STUDENT_EMAIL, password=VALID_PASSWORD, name="Alice"):
    return client.post(
        "/api/auth/register",
        json={"name": name, "email": email, "password": password},
    )


def _login(client, email=STUDENT_EMAIL, password=VALID_PASSWORD):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )


def _get_token(client, email=STUDENT_EMAIL, password=VALID_PASSWORD):
    """Register (if needed), verify and log in; return the access_token string."""
    _register(client, email=email, password=password)
    # Manually flip is_verified in the DB by using the db session via the test_user approach.
    # Instead, we call the login endpoint directly but first need a verified user.
    # This helper is only used alongside the test_user fixture below.
    resp = _login(client, email=email, password=password)
    return resp.json().get("access_token")


# ---------------------------------------------------------------------------
# Registration tests
# ---------------------------------------------------------------------------


class TestRegister:
    def test_happy_path_register_returns_201_and_user_read(self, client):
        """
        Happy-path registration should return 201 with a UserRead payload.
        password_hash must NOT appear in the response body.
        Validates: Requirement 3.1
        """
        resp = _register(client)
        assert resp.status_code == 201

        body = resp.json()
        # Core UserRead fields must be present
        assert body["email"] == STUDENT_EMAIL
        assert "id" in body
        assert "role" in body
        assert "is_verified" in body
        assert "campus_score" in body
        assert "created_at" in body

        # Sensitive field must NOT be exposed
        assert "password_hash" not in body

    def test_duplicate_email_returns_409(self, client):
        """
        Registering the same email twice must return 409.
        Validates: Requirement 3.2
        """
        _register(client)
        resp = _register(client)
        assert resp.status_code == 409
        assert resp.json()["detail"] == "Email already registered"

    def test_non_mits_domain_returns_422(self, client):
        """
        An email with a non-MITS domain must be rejected with 422.
        Validates: Requirement 2.3
        """
        resp = _register(client, email="user@gmail.com")
        assert resp.status_code == 422

    def test_short_password_returns_422(self, client):
        """
        A password shorter than 8 characters must trigger a 422 validation error.
        Validates: Requirement 3.3
        """
        resp = _register(client, password="short")
        assert resp.status_code == 422

    def test_student_domain_assigns_student_role(self, client):
        """
        Email with domain mitsgwl.ac.in must receive the STUDENT role.
        Validates: Requirement 2.1
        """
        resp = _register(client, email=STUDENT_EMAIL)
        assert resp.status_code == 201
        assert resp.json()["role"] == "STUDENT"

    def test_faculty_domain_assigns_faculty_role(self, client):
        """
        Email with domain mitsgwalior.in must receive the FACULTY role.
        Validates: Requirement 2.2
        """
        resp = _register(client, email=FACULTY_EMAIL, name="Bob")
        assert resp.status_code == 201
        assert resp.json()["role"] == "FACULTY"


# ---------------------------------------------------------------------------
# Login tests
# ---------------------------------------------------------------------------


class TestLogin:
    def test_valid_login_returns_200_and_token(self, client, test_user):
        """
        Logging in with valid credentials for a verified user must return 200 + Token.
        Validates: Requirement 6.1
        """
        resp = _login(client, email=test_user.email, password="testpass123")
        assert resp.status_code == 200

        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        assert isinstance(body["access_token"], str)
        assert len(body["access_token"]) > 0

    def test_unknown_email_returns_401(self, client):
        """
        Login with an email that does not exist must return 401.
        Validates: Requirement 6.2
        """
        resp = _login(client, email="nobody@mitsgwl.ac.in", password=VALID_PASSWORD)
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid credentials"

    def test_wrong_password_returns_401(self, client, test_user):
        """
        Login with the correct email but wrong password must return 401.
        Validates: Requirement 6.3
        """
        resp = _login(client, email=test_user.email, password="wrongpassword!")
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid credentials"

    def test_unverified_user_returns_403(self, client):
        """
        Login for a user whose is_verified == False must return 403.
        Validates: Requirement 6.4
        """
        # Register a fresh user — is_verified defaults to False
        email = "unverified@mitsgwl.ac.in"
        _register(client, email=email, password=VALID_PASSWORD, name="Unverified")

        resp = _login(client, email=email, password=VALID_PASSWORD)
        assert resp.status_code == 403
        assert resp.json()["detail"] == "Email not verified"


# ---------------------------------------------------------------------------
# GET /api/auth/me tests
# ---------------------------------------------------------------------------


class TestGetMe:
    def _obtain_token(self, client, test_user):
        """Log in with the verified test_user and return the access token string."""
        resp = _login(client, email=test_user.email, password="testpass123")
        assert resp.status_code == 200, f"Login failed: {resp.json()}"
        return resp.json()["access_token"]

    def test_get_me_with_valid_token_returns_200(self, client, test_user):
        """
        GET /api/auth/me with a valid Bearer token must return 200 + UserRead.
        Validates: Requirement 7.1
        """
        token = self._obtain_token(client, test_user)
        resp = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

        body = resp.json()
        assert body["email"] == test_user.email
        assert body["role"] == test_user.role
        assert "password_hash" not in body

    def test_get_me_without_token_returns_401(self, client):
        """
        GET /api/auth/me without an Authorization header must return 401.
        Validates: Requirement 7.2
        """
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_get_me_with_invalid_token_returns_401(self, client):
        """
        GET /api/auth/me with a forged / invalid token must return 401.
        Validates: Requirement 7.3
        """
        resp = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer this.is.not.a.valid.jwt"},
        )
        assert resp.status_code == 401
