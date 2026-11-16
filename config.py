import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "campusfix-default-secret-key-2026")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Ensure data directory exists
    DATA_DIR = BASE_DIR / "data"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{DATA_DIR / 'campusfix.db'}"
    )

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    ENV = "development"

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    ENV = "production"
    # In production, require explicit secret key or fallback securely
    SECRET_KEY = os.getenv("SECRET_KEY", "prod-campusfix-secure-key-replace-me")

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
