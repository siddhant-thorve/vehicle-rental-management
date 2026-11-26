import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-jwt-key-for-rental-microservices")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/rental_catalog_db",
)
