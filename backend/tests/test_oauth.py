import pytest
from unittest.mock import patch
from app.models.user import User, AuthProvider
from app.auth.password import verify_password

# Mock payloads
GOOGLE_STUDENT_PAYLOAD = {
    "email": "student_test@mitsgwl.ac.in",
    "name": "Test Student",
    "picture": "http://photo.com/pic.jpg",
    "sub": "google_student_sub_123"
}

GOOGLE_FACULTY_PAYLOAD = {
    "email": "faculty_test@mitsgwalior.in",
    "name": "Test Faculty",
    "picture": "http://photo.com/pic.jpg",
    "sub": "google_faculty_sub_456"
}

GOOGLE_OUTSIDER_PAYLOAD = {
    "email": "outsider@gmail.com",
    "name": "Outsider",
    "picture": "http://photo.com/pic.jpg",
    "sub": "google_outsider_sub_789"
}


@patch("app.routers.auth.verify_google_token")
def test_google_login_new_student_success(mock_verify, client, db):
    """
    Test that signing in via Google with a new student email creates the user,
    assigns the STUDENT role, marks verified, and returns is_new_user = True.
    """
    mock_verify.return_value = GOOGLE_STUDENT_PAYLOAD

    response = client.post(
        "/api/auth/google-login",
        json={"credential_token": "valid_mock_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["is_new_user"] is True

    # Check database
    user = db.query(User).filter(User.email == GOOGLE_STUDENT_PAYLOAD["email"]).first()
    assert user is not None
    assert user.role == "STUDENT"
    assert user.google_id == GOOGLE_STUDENT_PAYLOAD["sub"]
    assert user.auth_provider == "GOOGLE"
    assert user.is_verified is True
    assert user.profile_photo == GOOGLE_STUDENT_PAYLOAD["picture"]
    assert user.password_hash is None


@patch("app.routers.auth.verify_google_token")
def test_google_login_new_faculty_success(mock_verify, client, db):
    """
    Test that signing in via Google with a new faculty email creates the user
    and assigns the FACULTY role.
    """
    mock_verify.return_value = GOOGLE_FACULTY_PAYLOAD

    response = client.post(
        "/api/auth/google-login",
        json={"credential_token": "valid_mock_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_new_user"] is True

    user = db.query(User).filter(User.email == GOOGLE_FACULTY_PAYLOAD["email"]).first()
    assert user is not None
    assert user.role == "FACULTY"
    assert user.auth_provider == "GOOGLE"


@patch("app.routers.auth.verify_google_token")
def test_google_login_invalid_domain(mock_verify, client, db):
    """
    Test that registering/logging in with a non-MITS domain gets rejected with 422.
    """
    mock_verify.return_value = GOOGLE_OUTSIDER_PAYLOAD

    response = client.post(
        "/api/auth/google-login",
        json={"credential_token": "valid_mock_token"}
    )
    assert response.status_code == 422
    assert "not allowed" in response.json()["detail"]


@patch("app.routers.auth.verify_google_token")
def test_google_login_existing_email_linking(mock_verify, client, db):
    """
    Test that when an existing email user signs in via Google, the accounts link,
    auth_provider becomes BOTH, is_verified becomes True, and is_new_user is False.
    """
    # Create existing email user
    client.post(
        "/api/auth/register",
        json={
            "name": "Existing Email User",
            "email": GOOGLE_STUDENT_PAYLOAD["email"],
            "password": "securepassword123"
        }
    )

    mock_verify.return_value = GOOGLE_STUDENT_PAYLOAD

    # Try Google Login with same email
    response = client.post(
        "/api/auth/google-login",
        json={"credential_token": "valid_mock_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_new_user"] is False

    user = db.query(User).filter(User.email == GOOGLE_STUDENT_PAYLOAD["email"]).first()
    assert user is not None
    assert user.google_id == GOOGLE_STUDENT_PAYLOAD["sub"]
    assert user.auth_provider == "BOTH"
    assert user.is_verified is True
    assert user.password_hash is not None  # Kept the original password


@patch("app.routers.auth.verify_google_token")
def test_set_backup_password_and_login(mock_verify, client, db):
    """
    Test setting a backup password for a Google-only user, transitioning provider
    to BOTH, and logging in with email + password successfully.
    """
    # 1. Sign up via Google
    mock_verify.return_value = GOOGLE_STUDENT_PAYLOAD
    g_res = client.post(
        "/api/auth/google-login",
        json={"credential_token": "valid_mock_token"}
    )
    token = g_res.json()["access_token"]

    # 2. Try email/password login before setting password (should fail 401)
    login_res = client.post(
        "/api/auth/login",
        json={
            "email": GOOGLE_STUDENT_PAYLOAD["email"],
            "password": "backup_password_123"
        }
    )
    assert login_res.status_code == 401

    # 3. Set backup password
    set_res = client.post(
        "/api/auth/set-password",
        json={"password": "backup_password_123"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert set_res.status_code == 200
    
    # 4. Check DB status
    user = db.query(User).filter(User.email == GOOGLE_STUDENT_PAYLOAD["email"]).first()
    assert user.auth_provider == "BOTH"
    assert user.password_hash is not None
    assert verify_password("backup_password_123", user.password_hash)

    # 5. Login with email + password should now succeed
    login_res2 = client.post(
        "/api/auth/login",
        json={
            "email": GOOGLE_STUDENT_PAYLOAD["email"],
            "password": "backup_password_123"
        }
    )
    assert login_res2.status_code == 200
    assert "access_token" in login_res2.json()
