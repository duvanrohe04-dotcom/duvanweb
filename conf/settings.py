from flask import blueprints
import os
import secrets
import warnings
from dotenv import load_dotenv

load_dotenv()

def _ensure(var_name, default_factory):
    val = os.getenv(var_name)
    if val:
        return val
    generated = default_factory()
    warnings.warn(f"{var_name} no configurado. Se generó uno automáticamente. Defínelo en Coolify para producción.")
    return generated

class Config:
    SECRET_KEY = _ensure("SECRET_KEY", lambda: secrets.token_hex(32))
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
    _db_url = os.getenv('DATABASE_URL')
    if not _db_url:
        user = os.getenv('POSTGRES_USER')
        password = os.getenv('POSTGRES_PASSWORD')
        host = os.getenv('POSTGRES_HOST', '178.238.238.248')
        port = os.getenv('POSTGRES_PORT', '5051')
        db_name = os.getenv('POSTGRES_DB')
        
        if all([user, password, host, db_name]):
            from urllib.parse import quote_plus
            password_encoded = quote_plus(password)
            _db_url = f"postgresql+psycopg2://{user}:{password_encoded}@{host}:{port}/{db_name}"
            print(_db_url, flush=True)

    if _db_url and _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = _db_url or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

def get_config():
    env = os.getenv('FLASK_ENV', 'production')
    return DevelopmentConfig if env == 'development' else ProductionConfig
