from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.auth.password import hash_password, verify_password
from app.models.user import User, UserRole

# Mapping of allowed email domains to their assigned roles
ALLOWED_DOMAINS: dict[str, UserRole] = {
    "mitsgwl.ac.in": UserRole.STUDENT,
    "mitsgwalior.in": UserRole.FACULTY,
}


def resolve_role(email: str) -> UserRole:
    """
    Determine the UserRole from an email address by inspecting its domain.

    Splits at '@', lowercases the domain portion, and looks it up in
    ALLOWED_DOMAINS.  Raises ValueError for any domain not in the allow-list.
    """
    parts = email.split("@")
    if len(parts) != 2:
        raise ValueError("Email domain not allowed")
    domain = parts[1].lower()
    if domain not in ALLOWED_DOMAINS:
        raise ValueError("Email domain not allowed")
    return ALLOWED_DOMAINS[domain]


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, name: str | None, email: str, password: str) -> User:
    """
    Create a new user record.

    - Resolves the role from the email domain; raises HTTP 422 for unknown domains.
    - Raises HTTP 409 if the email is already registered.
    - Hashes the password with bcrypt before persisting.
    """
    # Resolve role — convert ValueError to HTTP 422
    try:
        role = resolve_role(email)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    # Check for duplicate email — HTTP 409
    existing = get_user_by_email(db, email)
    if existing is not None:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=role.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Verify credentials and return the User if they are correct.

    Returns None for an unknown email or a wrong password.
    The caller is responsible for checking user.is_verified.
    """
    user = get_user_by_email(db, email)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def verify_otp(db: Session, email: str, otp: str) -> bool:
    """Verify a one-time password for the given email (retained for future sprints)."""
    user = get_user_by_email(db, email)
    if not user:
        return False
    if user.otp_code == otp:
        user.is_verified = True
        user.otp_code = None
        db.add(user)
        db.commit()
        db.refresh(user)
        return True
    return False
