import hmac
import time
import threading
from collections import defaultdict, deque
from functools import wraps
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, jsonify, session, current_app
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from models.models import Client, Project, Message, PortfolioItem, PublicReview, Setting, Visit

main_bp = Blueprint('main', __name__)

_stats_cache = {'timestamp': 0, 'data': None}

ADMIN_USER = 'admin'
ALLOWED_SETTINGS = {
    'dr_wa', 'dr_tagline', 'dr_footer_1', 'dr_footer_2',
    'dr_social_ig', 'dr_social_tt', 'dr_income', 'dr_admin_pass',
}

# --- Rate limiting (en memoria, por proceso) ---
_attempts = defaultdict(deque)
_attempts_lock = threading.Lock()


def _rate_limited(bucket, ip, limit, window):
    """True si `ip` ya alcanzó `limit` eventos en los últimos `window` segundos."""
    now = time.time()
    key = (bucket, ip)
    with _attempts_lock:
        q = _attempts[key]
        while q and now - q[0] > window:
            q.popleft()
        if not q:
            _attempts.pop(key, None)  # evita que el dict crezca con cada IP vista
        return len(q) >= limit


def _register_attempt(bucket, ip):
    with _attempts_lock:
        _attempts[(bucket, ip)].append(time.time())


def _clear_attempts(bucket, ip):
    with _attempts_lock:
        _attempts.pop((bucket, ip), None)


# --- Helpers ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'error': 'No autorizado. Inicie sesión.'}), 401
        return f(*args, **kwargs)
    return decorated_function


def _json():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def _text(value, max_len):
    if value is None:
        return None
    return str(value).strip()[:max_len]


def _int(value, default=0, lo=None, hi=None):
    try:
        n = int(value)
    except (TypeError, ValueError):
        n = default
    if lo is not None:
        n = max(lo, n)
    if hi is not None:
        n = min(hi, n)
    return n


def _error(e, status=500):
    db.session.rollback()
    current_app.logger.exception('Error en API: %s', e)
    return jsonify({'success': False, 'error': 'Error interno del servidor.'}), status


def _upsert(model, data):
    """Devuelve la fila a editar (si viene id y existe) o una nueva. No fuerza ids ajenos."""
    row_id = _int(data.get('id'), default=0)
    row = db.session.get(model, row_id) if row_id else None
    if row is None:
        row = model()
        db.session.add(row)
    return row


def _delete(model, row_id):
    try:
        row = db.session.get(model, row_id)
        if row:
            db.session.delete(row)
            db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return _error(e)


def _verify_admin_password(candidate):
    """Valida la contraseña; migra hashes legacy en texto plano al primer login correcto."""
    setting = db.session.get(Setting, 'dr_admin_pass')
    stored = setting.value if setting and setting.value else 'admin123'
    if stored.startswith(('pbkdf2:', 'scrypt:')):
        return check_password_hash(stored, candidate)
    ok = hmac.compare_digest(stored.encode('utf-8'), candidate.encode('utf-8'))
    if ok:
        if setting is None:
            setting = Setting(key='dr_admin_pass')
            db.session.add(setting)
        setting.value = generate_password_hash(candidate)
        db.session.commit()
    return ok


def _async_record_visit(app, ip, user_agent):
    with app.app_context():
        try:
            db.session.add(Visit(ip=ip, user_agent=user_agent))
            db.session.commit()

            # Poda automática si hay más de 10.000 visitas para mantener la BD pequeña.
            if Visit.query.count() > 10000:
                cutoff = datetime.utcnow() - timedelta(days=30)
                Visit.query.filter(Visit.timestamp < cutoff).delete()
                db.session.commit()
        except Exception:
            db.session.rollback()
        finally:
            db.session.remove()


@main_bp.route('/')
def index():
    try:
        ip = (request.remote_addr or '')[:60]  # ProxyFix ya resolvió X-Forwarded-For
        user_agent = (request.headers.get('User-Agent') or '')[:500]
        app = current_app._get_current_object()
        threading.Thread(target=_async_record_visit, args=(app, ip, user_agent), daemon=True).start()
    except Exception:
        pass
    return render_template('index.html')


@main_bp.route('/admin')
@main_bp.route('/admin/')
def admin_page():
    """Único acceso al panel: abre el login (o el panel si ya hay sesión)."""
    resp = current_app.make_response(render_template('index.html', open_admin=True))
    resp.headers['Cache-Control'] = 'no-store'
    return resp


# --- AUTH ROUTES ---

@main_bp.route('/api/login', methods=['POST'])
def login():
    ip = request.remote_addr or ''
    try:
        if _rate_limited('login', ip, 5, 300):
            return jsonify({'success': False, 'error': 'Demasiados intentos. Espera 5 minutos.'}), 429
        data = _json()
        user = (data.get('user') or '').strip()
        password = (data.get('password') or '').strip()

        if user == ADMIN_USER and _verify_admin_password(password):
            _clear_attempts('login', ip)
            session.clear()
            session['admin_logged_in'] = True
            return jsonify({'success': True, 'message': 'Sesión iniciada correctamente.'})
        _register_attempt('login', ip)
        return jsonify({'success': False, 'error': 'Usuario o contraseña incorrectos.'}), 401
    except Exception as e:
        return _error(e)


@main_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})


@main_bp.route('/api/check_auth', methods=['GET'])
def check_auth():
    return jsonify({'authenticated': bool(session.get('admin_logged_in'))})


# --- API ROUTES ---

@main_bp.route('/api/init', methods=['GET'])
def get_init_data():
    try:
        authed = bool(session.get('admin_logged_in'))
        settings = Setting.query.all()
        # Nunca exponer la contraseña (ni su hash).
        settings_dict = {s.key: s.value for s in settings if s.key != 'dr_admin_pass'}
        reviews = PublicReview.query.all()
        portfolio = PortfolioItem.query.all()

        payload = {
            'success': True,
            'clients': [],
            'projects': [],
            'messages': [],
            'portfolio': [{'id': p.id, 'title': p.title, 'desc': p.desc, 'url': p.url, 'link': p.link} for p in portfolio],
            'reviews': [{'id': r.id, 'initials': r.initials, 'stars': r.stars, 'name': r.name, 'biz': r.biz, 'text': r.text} for r in reviews],
            'settings': settings_dict,
            'stats': {'total_visits': 0, 'today_visits': 0, 'device_stats': {'mobile': 0, 'desktop': 0}, 'recent_visits': []},
            'authenticated': authed,
        }

        # Datos privados (clientes, proyectos, mensajes, visitas) solo para el admin.
        if authed:
            payload['clients'] = [{'id': c.id, 'name': c.name, 'biz': c.biz, 'phone': c.phone, 'service': c.service, 'status': c.status, 'date': c.date} for c in Client.query.all()]
            payload['projects'] = [{'id': p.id, 'client': p.client, 'type': p.type, 'start': p.start, 'end': p.end, 'status': p.status, 'progress': p.progress} for p in Project.query.all()]
            payload['messages'] = [{'id': m.id, 'name': m.name, 'phone': m.phone, 'msg': m.msg, 'status': m.status} for m in Message.query.all()]
            payload['stats'] = get_stats()
        return jsonify(payload)
    except Exception as e:
        return _error(e)


def get_stats():
    now = time.time()
    if _stats_cache['data'] and (now - _stats_cache['timestamp'] < 15):
        return _stats_cache['data']
    try:
        total = Visit.query.count()
        now_col = datetime.utcnow() - timedelta(hours=5)  # Colombia (UTC-5)
        today_start_col = now_col.replace(hour=0, minute=0, second=0, microsecond=0)
        today_start_utc = today_start_col + timedelta(hours=5)
        today = Visit.query.filter(Visit.timestamp >= today_start_utc).count()

        all_visits = Visit.query.order_by(Visit.timestamp.desc()).limit(100).all()
        mobile = 0
        desktop = 0
        for v in all_visits:
            ua = (v.user_agent or '').lower()
            if 'mobile' in ua or 'android' in ua or 'iphone' in ua:
                mobile += 1
            else:
                desktop += 1

        recent = [{
            'ip': v.ip,
            'ua': v.user_agent or '',
            'time': (v.timestamp - timedelta(hours=5)).strftime('%H:%M:%S') if v.timestamp else '',
        } for v in all_visits[:10]]

        res = {
            'total_visits': total,
            'today_visits': today,
            'device_stats': {'mobile': mobile, 'desktop': desktop},
            'recent_visits': recent,
        }
        _stats_cache['timestamp'] = now
        _stats_cache['data'] = res
        return res
    except Exception as e:
        current_app.logger.error('Error getting stats: %s', e)
        return _stats_cache['data'] or {'total_visits': 0, 'today_visits': 0, 'device_stats': {'mobile': 0, 'desktop': 0}, 'recent_visits': []}


@main_bp.route('/api/clients', methods=['POST'])
@login_required
def save_client():
    try:
        data = _json()
        name = _text(data.get('name'), 100)
        if not name:
            return jsonify({'success': False, 'error': 'El nombre es obligatorio.'}), 400
        client = _upsert(Client, data)
        client.name = name
        client.biz = _text(data.get('biz'), 100)
        client.phone = _text(data.get('phone'), 20)
        client.service = _text(data.get('service'), 100)
        client.status = _text(data.get('status'), 50)
        client.date = _text(data.get('date'), 20)
        db.session.commit()
        return jsonify({'success': True, 'id': client.id})
    except Exception as e:
        return _error(e)


@main_bp.route('/api/clients/<int:id>', methods=['DELETE'])
@login_required
def delete_client(id):
    return _delete(Client, id)


@main_bp.route('/api/projects', methods=['POST'])
@login_required
def save_project():
    try:
        data = _json()
        project = _upsert(Project, data)
        project.client = _text(data.get('client'), 100)
        project.type = _text(data.get('type'), 100)
        project.start = _text(data.get('start'), 20)
        project.end = _text(data.get('end'), 20)
        project.status = _text(data.get('status'), 50)
        project.progress = _int(data.get('progress'), 0, 0, 100)
        db.session.commit()
        return jsonify({'success': True, 'id': project.id})
    except Exception as e:
        return _error(e)


@main_bp.route('/api/projects/<int:id>', methods=['DELETE'])
@login_required
def delete_project(id):
    return _delete(Project, id)


@main_bp.route('/api/messages', methods=['POST'])
def save_message():
    try:
        data = _json()
        msg_id = _int(data.get('id'), 0)
        if msg_id or 'status' in data:
            # Edición desde el panel: requiere sesión.
            if not session.get('admin_logged_in'):
                return jsonify({'success': False, 'error': 'No autorizado.'}), 401
            msg = _upsert(Message, data)
            if 'name' in data: msg.name = _text(data.get('name'), 100)
            if 'phone' in data: msg.phone = _text(data.get('phone'), 20)
            if 'msg' in data: msg.msg = _text(data.get('msg'), 2000)
            if 'status' in data: msg.status = _text(data.get('status'), 50)
        else:
            # Formulario de contacto público.
            ip = request.remote_addr or ''
            if _rate_limited('message', ip, 5, 600):
                return jsonify({'success': False, 'error': 'Demasiados mensajes. Intenta más tarde.'}), 429
            name = _text(data.get('name'), 100) or ''
            phone = _text(data.get('phone'), 20) or ''
            msg_text = _text(data.get('msg'), 2000) or ''
            if not name or not phone:
                return jsonify({'success': False, 'error': 'Nombre y teléfono son obligatorios.'}), 400
            _register_attempt('message', ip)
            msg = Message(name=name, phone=phone, msg=msg_text, status='Nuevo')
            db.session.add(msg)

        db.session.commit()
        return jsonify({'success': True, 'id': msg.id})
    except Exception as e:
        return _error(e)


@main_bp.route('/api/messages/<int:id>', methods=['DELETE'])
@login_required
def delete_message(id):
    return _delete(Message, id)


@main_bp.route('/api/portfolio', methods=['POST'])
@login_required
def save_portfolio():
    try:
        data = _json()
        p = _upsert(PortfolioItem, data)
        p.title = _text(data.get('title'), 100)
        p.desc = _text(data.get('desc'), 255)
        p.url = _text(data.get('url'), 255)
        p.link = _text(data.get('link'), 255)
        db.session.commit()
        return jsonify({'success': True, 'id': p.id})
    except Exception as e:
        return _error(e)


@main_bp.route('/api/portfolio/<int:id>', methods=['DELETE'])
@login_required
def delete_portfolio(id):
    return _delete(PortfolioItem, id)


@main_bp.route('/api/reviews', methods=['POST'])
def save_review():
    """Visitantes pueden enviar una reseña nueva; editar requiere sesión de admin."""
    try:
        data = _json()
        is_admin = bool(session.get('admin_logged_in'))
        if _int(data.get('id'), 0) and not is_admin:
            return jsonify({'success': False, 'error': 'No autorizado.'}), 401

        if not is_admin:
            ip = request.remote_addr or ''
            if _rate_limited('review', ip, 3, 3600):
                return jsonify({'success': False, 'error': 'Demasiadas reseñas. Intenta más tarde.'}), 429

        name = _text(data.get('name'), 100)
        text = _text(data.get('text'), 1000)
        if not name or not text:
            return jsonify({'success': False, 'error': 'Nombre y reseña son obligatorios.'}), 400

        r = _upsert(PublicReview, data) if is_admin else PublicReview()
        if not is_admin:
            db.session.add(r)
            _register_attempt('review', request.remote_addr or '')
        r.initials = _text(data.get('initials'), 10) or 'CL'
        r.stars = _int(data.get('stars'), 5, 1, 5)
        r.name = name
        r.biz = _text(data.get('biz'), 100)
        r.text = text
        db.session.commit()
        return jsonify({'success': True, 'id': r.id})
    except Exception as e:
        return _error(e)


@main_bp.route('/api/reviews/<int:id>', methods=['DELETE'])
@login_required
def delete_review(id):
    return _delete(PublicReview, id)


@main_bp.route('/api/visits', methods=['DELETE'])
@login_required
def reset_visits():
    try:
        Visit.query.delete()
        _stats_cache['data'] = None
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return _error(e)


@main_bp.route('/api/settings', methods=['POST'])
@login_required
def save_settings():
    try:
        data = _json()
        for key, value in data.items():
            if key not in ALLOWED_SETTINGS:
                continue
            value = str(value if value is not None else '')
            if key == 'dr_admin_pass':
                if len(value) < 4:
                    return jsonify({'success': False, 'error': 'La contraseña debe tener al menos 4 caracteres.'}), 400
                value = generate_password_hash(value)
            else:
                value = value[:2000]
            setting = db.session.get(Setting, key)
            if setting:
                setting.value = value
            else:
                db.session.add(Setting(key=key, value=value))
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return _error(e)
