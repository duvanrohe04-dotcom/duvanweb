import os
import secrets
import warnings
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def _secret_key():
    """SECRET_KEY de entorno; si falta, se genera UNA vez y se guarda en disco.

    Con varios workers de gunicorn una clave aleatoria por proceso invalidaba
    las sesiones del admin de forma intermitente.
    """
    val = os.getenv("SECRET_KEY")
    if val:
        return val
    key_file = os.path.join(os.path.dirname(_db_path()), '.secret_key')
    try:
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        if os.path.exists(key_file):
            with open(key_file, 'r', encoding='utf-8') as fh:
                stored = fh.read().strip()
            if stored:
                return stored
        generated = secrets.token_hex(32)
        with open(key_file, 'w', encoding='utf-8') as fh:
            fh.write(generated)
        warnings.warn("SECRET_KEY no configurado. Se generó uno y se guardó junto a la base de datos.")
        return generated
    except OSError:
        warnings.warn("SECRET_KEY no configurado y no se pudo persistir. Defínelo en Coolify.")
        return secrets.token_hex(32)


def _db_path():
    """Ruta absoluta del archivo SQLite (DATABASE_PATH o instance/duvan_web.db)."""
    path = os.getenv('DATABASE_PATH') or os.path.join(BASE_DIR, 'instance', 'duvan_web.db')
    if not os.path.isabs(path):
        path = os.path.join(BASE_DIR, path)
    return path


class Config:
    SECRET_KEY = _secret_key()
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
    SITE_NAME = os.getenv('SITE_NAME', 'Duvan Rodriguez')
    SITE_URL = os.getenv('SITE_URL', 'https://duvanweb.com')

    DATABASE_FILE = _db_path()
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_FILE.replace('\\', '/')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "connect_args": {"timeout": 30},
    }

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', '0') == '1'
    MAX_CONTENT_LENGTH = 1024 * 1024


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


def get_config():
    env = os.getenv('FLASK_ENV', 'production')
    return DevelopmentConfig if env == 'development' else ProductionConfig
