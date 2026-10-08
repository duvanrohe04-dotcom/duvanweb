import os
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# La config lee el entorno al importarse: apuntar a una BD temporal ANTES de importar la app.
_tmp = tempfile.mkdtemp(prefix='duvan_test_')
os.environ['DATABASE_PATH'] = os.path.join(_tmp, 'test.db')
os.environ['SECRET_KEY'] = 'test-secret'
os.environ['FLASK_ENV'] = 'production'


@pytest.fixture()
def app():
    from app import create_app
    from extensions import db
    from routes import main as main_routes

    application = create_app()
    application.config['TESTING'] = True
    main_routes._attempts.clear()
    main_routes._stats_cache.update({'timestamp': 0, 'data': None})
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin(app):
    c = app.test_client()
    r = c.post('/api/login', json={'user': 'admin', 'password': 'admin123'})
    assert r.status_code == 200
    return c

