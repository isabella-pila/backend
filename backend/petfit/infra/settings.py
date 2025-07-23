from dotenv import load_dotenv
import os

load_dotenv()

DOCKER_ENV = os.getenv("DOCKER_ENV", "0") == "1"

POSTGRES_USER = os.getenv("POSTGRES_USER","petfit")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "petfitpass")
POSTGRES_DB = os.getenv("POSTGRES_DB", "petfitdb")
POSTGRES_HOST = "db" if DOCKER_ENV else "localhost"
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"