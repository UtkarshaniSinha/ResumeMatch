import os

from dotenv import load_dotenv

# loads values from .env (only on my laptop, the server has real env variables)
load_dotenv()

DEV_SECRET_KEY = "dev-only-not-secret"


def get_database_url():
    # sqlite locally, postgres on the server
    url = os.environ.get("DATABASE_URL") or "sqlite:///resumematch.db"
    # some providers give postgres:// but sqlalchemy needs postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or DEV_SECRET_KEY
    SQLALCHEMY_DATABASE_URI = get_database_url()

    # cloud databases close idle connections, this checks before using one
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # whole request max 3 MB (pdf itself is limited to 2 MB in pdf_reader.py,
    # extra space is for the job description text)
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024

    SESSION_COOKIE_HTTPONLY = True   # javascript can't read the cookie
    SESSION_COOKIE_SAMESITE = "Lax"  # cookie not sent with forms from other sites
    SESSION_COOKIE_SECURE = False    # True in production (https only)

    IS_PRODUCTION = False


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    IS_PRODUCTION = True


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False  # turned on again in the csrf test


def choose_config():
    if os.environ.get("APP_ENV") == "production":
        return ProductionConfig
    return Config
