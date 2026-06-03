import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/campushub")
SECRET_KEY = os.getenv("SECRET_KEY", "replace-me")
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL", "")
