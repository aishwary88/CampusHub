import os
from google.oauth2 import id_token
from google.auth.transport import requests
from dotenv import load_dotenv

load_dotenv()

# Retrieve Google Client ID from environment. Support both backend and frontend naming conventions.
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID") or os.getenv("VITE_GOOGLE_CLIENT_ID")

def verify_google_token(token: str) -> dict:
    """
    Verify the Google ID token sent from the frontend.
    Returns the decoded token payload (which includes 'sub', 'email', 'name', 'picture').
    Raises ValueError if token is invalid or GOOGLE_CLIENT_ID is not configured.
    """
    if not GOOGLE_CLIENT_ID:
        # Fallback for local development/testing without client ID configured
        # In a real setup, we would raise an error, but let's allow a test mode or check it.
        # Let's raise ValueError to ensure security unless it's a test token.
        raise ValueError("GOOGLE_CLIENT_ID is not configured on the backend.")

    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        return idinfo
    except ValueError as e:
        raise ValueError(f"Invalid Google ID token: {str(e)}")
