from extensions import db
from models.models import Setting, Message, PublicReview


# ---------- Base de datos ----------
def test_uses_sqlite(app):
    assert app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:///')


def test_seed_is_idempotent(app):
    from seed import seed_defaults
    with app.app_context():
        seed_defaults()
        seed_defaults()
        assert PublicReview.query.count() == 3
        assert db.session.get(Setting, 'dr_wa').value == '3107480575'


def test_health(client):
    assert client.get('/health').get_json() == {'status': 'ok'}


def test_index_renders(client):
    r = client.get('/')
    assert r.status_code == 200


# ---------- Auth ----------
def test_login_ok_and_hash_stored(app, client):
    r = client.post('/api/login', json={'user': 'admin', 'password': 'admin123'})
    assert r.status_code == 200
    with app.app_context():
        stored = db.session.get(Setting, 'dr_admin_pass').value
        assert stored != 'admin' and stored.startswith(('pbkdf2:', 'scrypt:'))


def test_login_wrong_password(client):
    r = client.post('/api/login', json={'user': 'admin', 'password': 'nope'})
    assert r.status_code == 401


def test_legacy_plaintext_password_is_migrated(app, client):
    with app.app_context():
        db.session.get(Setting, 'dr_admin_pass').value = 'secreta1'
        db.session.commit()
    assert client.post('/api/login', json={'user': 'admin', 'password': 'secreta1'}).status_code == 200
    with app.app_context():
        assert db.session.get(Setting, 'dr_admin_pass').value.startswith(('pbkdf2:', 'scrypt:'))


def test_login_rate_limit(client):
    for _ in range(5):
        assert client.post('/api/login', json={'user': 'admin', 'password': 'x'}).status_code == 401
    assert client.post('/api/login', json={'user': 'admin', 'password': 'admin123'}).status_code == 429


def test_logout(admin):
    admin.post('/api/logout')
    assert admin.get('/api/check_auth').get_json()['authenticated'] is False


def test_change_password(admin, app):
    r = admin.post('/api/settings', json={'dr_admin_pass': 'nueva-clave'})
    assert r.status_code == 200
    fresh = app.test_client()
    assert fresh.post('/api/login', json={'user': 'admin', 'password': 'admin123'}).status_code == 401
    assert fresh.post('/api/login', json={'user': 'admin', 'password': 'nueva-clave'}).status_code == 200


# ---------- Privacidad de /api/init ----------
def test_init_public_hides_private_data(app, client, admin):
    admin.post('/api/clients', json={'name': 'Secreto', 'phone': '3000000000'})
    admin.post('/api/messages', json={'id': 0, 'status': 'Nuevo', 'name': 'X', 'phone': '1', 'msg': 'privado'})
    data = client.get('/api/init').get_json()
    assert data['clients'] == [] and data['messages'] == [] and data['projects'] == []
    assert data['authenticated'] is False
    assert 'dr_admin_pass' not in data['settings']
    assert len(data['reviews']) == 3


def test_init_admin_sees_everything(admin):
    admin.post('/api/clients', json={'name': 'Cliente A', 'phone': '3001112222'})
    data = admin.get('/api/init').get_json()
    assert [c['name'] for c in data['clients']] == ['Cliente A']
    assert 'dr_admin_pass' not in data['settings']


# ---------- Protección de rutas ----------
def test_protected_routes_require_login(client):
    for method, url in [('post', '/api/clients'), ('post', '/api/projects'), ('post', '/api/portfolio'),
                        ('post', '/api/settings'), ('delete', '/api/clients/1'), ('delete', '/api/visits'),
                        ('delete', '/api/reviews/1'), ('delete', '/api/messages/1')]:
        r = getattr(client, method)(url, json={})
        assert r.status_code == 401, url


# ---------- CRUD (accesos del panel) ----------
def test_client_crud(admin):
    r = admin.post('/api/clients', json={'name': 'Ana', 'biz': 'Tienda', 'phone': '300', 'service': 'Web', 'status': 'En proceso', 'date': '2026-01-01'})
    cid = r.get_json()['id']
    admin.post('/api/clients', json={'id': cid, 'name': 'Ana M', 'status': 'Entregado'})
    clients = admin.get('/api/init').get_json()['clients']
    assert len(clients) == 1 and clients[0]['name'] == 'Ana M' and clients[0]['status'] == 'Entregado'
    assert admin.delete(f'/api/clients/{cid}').get_json()['success']
    assert admin.get('/api/init').get_json()['clients'] == []


def test_client_requires_name(admin):
    assert admin.post('/api/clients', json={'biz': 'x'}).status_code == 400


def test_project_crud_and_progress_clamp(admin):
    pid = admin.post('/api/projects', json={'client': 'Ana', 'type': 'Web', 'progress': 999}).get_json()['id']
    p = admin.get('/api/init').get_json()['projects'][0]
    assert p['progress'] == 100
    admin.post('/api/projects', json={'id': pid, 'client': 'Ana', 'progress': 'abc'})
    assert admin.get('/api/init').get_json()['projects'][0]['progress'] == 0
    admin.delete(f'/api/projects/{pid}')
    assert admin.get('/api/init').get_json()['projects'] == []


def test_portfolio_crud(admin, client):
    pid = admin.post('/api/portfolio', json={'title': 'Sitio', 'desc': 'd', 'url': 'https://x/y.png', 'link': 'https://x'}).get_json()['id']
    assert client.get('/api/init').get_json()['portfolio'][0]['title'] == 'Sitio'
    admin.delete(f'/api/portfolio/{pid}')
    assert client.get('/api/init').get_json()['portfolio'] == []


def test_settings_whitelist_and_save(admin, client):
    admin.post('/api/settings', json={'dr_wa': '3201234567', 'evil_key': 'x'})
    s = client.get('/api/init').get_json()['settings']
    assert s['dr_wa'] == '3201234567' and 'evil_key' not in s


# ---------- Mensajes (formulario público) ----------
def test_public_message_flow(admin, client):
    r = client.post('/api/messages', json={'name': 'Visitante', 'phone': '3001', 'msg': 'Hola'})
    assert r.status_code == 200
    mid = r.get_json()['id']
    msgs = admin.get('/api/init').get_json()['messages']
    assert msgs[0]['status'] == 'Nuevo'
    # El visitante no puede cambiar el estado
    assert client.post('/api/messages', json={'id': mid, 'status': 'Cerrado'}).status_code == 401
    # El admin sí
    admin.post('/api/messages', json={'id': mid, 'status': 'Contactado'})
    assert admin.get('/api/init').get_json()['messages'][0]['status'] == 'Contactado'
    admin.delete(f'/api/messages/{mid}')
    assert admin.get('/api/init').get_json()['messages'] == []


def test_public_message_validation_and_rate_limit(client):
    assert client.post('/api/messages', json={'name': '', 'phone': ''}).status_code == 400
    for _ in range(5):
        assert client.post('/api/messages', json={'name': 'A', 'phone': '1'}).status_code == 200
    assert client.post('/api/messages', json={'name': 'A', 'phone': '1'}).status_code == 429


def test_message_does_not_force_ids(app, client):
    client.post('/api/messages', json={'name': 'A', 'phone': '1', 'msg': 'x'})
    with app.app_context():
        assert Message.query.count() == 1


# ---------- Reseñas públicas ----------
def test_public_can_submit_review_but_not_edit(admin, client):
    r = client.post('/api/reviews', json={'name': 'Pepe', 'text': 'Excelente', 'stars': 9, 'biz': 'N'})
    assert r.status_code == 200
    reviews = client.get('/api/init').get_json()['reviews']
    new = [x for x in reviews if x['name'] == 'Pepe'][0]
    assert new['stars'] == 5  # clamp
    assert client.post('/api/reviews', json={'id': new['id'], 'name': 'Hack', 'text': 'x'}).status_code == 401
    assert client.delete(f"/api/reviews/{new['id']}").status_code == 401
    assert admin.delete(f"/api/reviews/{new['id']}").get_json()['success']


def test_review_validation(client):
    assert client.post('/api/reviews', json={'name': '', 'text': ''}).status_code == 400


# ---------- Visitas ----------
def test_reset_visits(admin):
    assert admin.delete('/api/visits').get_json()['success']
    assert admin.get('/api/init').get_json()['stats']['total_visits'] == 0


def test_bad_json_does_not_crash(admin):
    r = admin.post('/api/clients', data='no-json', content_type='application/json')
    assert r.status_code == 400


# ---------- Acceso /admin ----------
def test_admin_route_opens_login(client):
    r = client.get('/admin')
    assert r.status_code == 200 and b'window.OPEN_ADMIN = true' in r.data


def test_public_page_has_no_hidden_admin_access(client):
    r = client.get('/')
    assert b'secret-btn' not in r.data and b'OPEN_ADMIN' not in r.data
    assert b'ctrlKey' not in client.get('/static/js/main.js').data


def test_old_user_rejected(client):
    assert client.post('/api/login', json={'user': 'duvan', 'password': 'admin123'}).status_code == 401


def test_existing_db_password_reset_once(app):
    from seed import seed_defaults, RESET_MARKER
    from werkzeug.security import generate_password_hash
    with app.app_context():
        db.session.delete(db.session.get(Setting, RESET_MARKER))
        db.session.get(Setting, 'dr_admin_pass').value = generate_password_hash('otra')
        db.session.commit()
        seed_defaults()
    assert app.test_client().post('/api/login', json={'user': 'admin', 'password': 'admin123'}).status_code == 200
