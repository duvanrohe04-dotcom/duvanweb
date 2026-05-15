import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY no esta configurado. Define SECRET_KEY en .env o variables de entorno.")
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
    if not ADMIN_PASSWORD:
        raise RuntimeError("ADMIN_PASSWORD no esta configurado. Define ADMIN_PASSWORD en .env o variables de entorno.")
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
    _db_url = os.getenv('DATABASE_URL')
    if _db_url:
        if _db_url.startswith("postgres://"):
            _db_url = _db_url.replace("postgres://", "postgresql://", 1)
        if "postgresql" in _db_url and "sslmode" not in _db_url:
            connector = "&" if "?" in _db_url else "?"
            _db_url = f"{_db_url}{connector}sslmode=require"
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
