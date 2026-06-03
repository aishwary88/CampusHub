from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserRead, Token, LoginRequest
from app.database.database import get_db
from app.services import auth_service
from app.auth import jwt_handler as jwt_utils
from app.auth.jwt import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    - Returns HTTP 201 with UserRead on success.
    - Returns HTTP 409 if the email is already registered (raised by auth_service).
    - Returns HTTP 422 if the email domain is not an allowed MITS domain (raised by auth_service).
    - Returns HTTP 422 if the password is shorter than 8 characters (Pydantic validation).
    """
    # auth_service.create_user raises HTTPException(409) for duplicate email
    # and HTTPException(422) for disallowed email domains.
    created = auth_service.create_user(
        db,
        name=user.name,
        email=user.email,
        password=user.password,
    )
    return created


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT.

    - Returns HTTP 200 with a Token on success.
    - Returns HTTP 401 if credentials are invalid (unknown email or wrong password).
    - Returns HTTP 403 if the account exists but has not been verified.
    """
    user = auth_service.authenticate_user(db, data.email, data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )
    token = jwt_utils.create_access_token(
        {"sub": user.email, "id": user.id, "role": user.role}
    )
    return Token(access_token=token, token_type="bearer")


@router.get("/me", response_model=UserRead)
def get_me(current_user=Depends(get_current_user)):
    """
    Return the profile of the currently authenticated user.

    - Returns HTTP 200 with UserRead for the bearer-token owner.
    - Returns HTTP 401 if no token or an invalid/expired token is provided
      (handled by get_current_user dependency).
    """
    return current_user
