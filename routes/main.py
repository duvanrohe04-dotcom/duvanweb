import time
import threading
from functools import wraps
from flask import Blueprint, render_template, request, jsonify, session, current_app
from extensions import db
from models.models import Client, Project, Message, PortfolioItem, PublicReview, Setting, Visit
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

_stats_cache = {'timestamp': 0, 'data': None}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'error': 'No autorizado. Inicie sesión.'}), 401
        return f(*args, **kwargs)
    return decorated_function

def _async_record_visit(app, ip, user_agent):
    with app.app_context():
        try:
            v = Visit(ip=ip, user_agent=user_agent)
            db.session.add(v)
            db.session.commit()
            
            # Auto-prune old visits if total count exceeds 10,000 to keep DB small and ultra-fast
            if Visit.query.count() > 10000:
                cutoff = datetime.utcnow() - timedelta(days=30)
                Visit.query.filter(Visit.timestamp < cutoff).delete()
                db.session.commit()
        except Exception as e:
            db.session.rollback()

@main_bp.route('/')
def index():
    try:
        ip = request.headers.get('X-Forwarded-For', request.remote_addr or '').split(',')[0].strip()
        user_agent = (request.headers.get('User-Agent') or '')[:500]
        app = current_app._get_current_object()
        threading.Thread(target=_async_record_visit, args=(app, ip, user_agent), daemon=True).start()
    except Exception as e:
        pass
    return render_template('index.html')

# --- AUTH ROUTES ---

@main_bp.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json or {}
        user = (data.get('user') or '').strip()
        password = (data.get('password') or '').strip()
        
        admin_setting = Setting.query.get('dr_admin_pass')
        valid_pass = admin_setting.value if admin_setting and admin_setting.value else 'admin'
        
        if user == 'duvan' and password == valid_pass:
            session['admin_logged_in'] = True
            return jsonify({'success': True, 'message': 'Sesión iniciada correctamente.'})
        else:
            return jsonify({'success': False, 'error': 'Usuario o contraseña incorrectos.'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/logout', methods=['POST'])
def logout():
    session.pop('admin_logged_in', None)
    return jsonify({'success': True})

@main_bp.route('/api/check_auth', methods=['GET'])
def check_auth():
    return jsonify({'authenticated': bool(session.get('admin_logged_in'))})

# --- API ROUTES ---

@main_bp.route('/api/init', methods=['GET'])
def get_init_data():
    try:
        clients = Client.query.all()
        projects = Project.query.all()
        messages = Message.query.all()
        portfolio = PortfolioItem.query.all()
        reviews = PublicReview.query.all()
        settings = Setting.query.all()
        
        # NEVER expose dr_admin_pass in public init endpoint
        settings_dict = {s.key: s.value for s in settings if s.key != 'dr_admin_pass'}
        
        # Visit Stats (Cached 15s in memory)
        stats = get_stats()
        
        return jsonify({
            'success': True,
            'clients': [{ 'id': c.id, 'name': c.name, 'biz': c.biz, 'phone': c.phone, 'service': c.service, 'status': c.status, 'date': c.date } for c in clients],
            'projects': [{ 'id': p.id, 'client': p.client, 'type': p.type, 'start': p.start, 'end': p.end, 'status': p.status, 'progress': p.progress } for p in projects],
            'messages': [{ 'id': m.id, 'name': m.name, 'phone': m.phone, 'msg': m.msg, 'status': m.status } for m in messages],
            'portfolio': [{ 'id': p.id, 'title': p.title, 'desc': p.desc, 'url': p.url, 'link': p.link } for p in portfolio],
            'reviews': [{ 'id': r.id, 'initials': r.initials, 'stars': r.stars, 'name': r.name, 'biz': r.biz, 'text': r.text } for r in reviews],
            'settings': settings_dict,
            'stats': stats,
            'authenticated': bool(session.get('admin_logged_in'))
        })
    except Exception as e:
        print(f"API Init error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def get_stats():
    now = time.time()
    if _stats_cache['data'] and (now - _stats_cache['timestamp'] < 15):
        return _stats_cache['data']
    try:
        total = Visit.query.count()
        now_col = datetime.utcnow() - timedelta(hours=5)
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
        
        recent = []
        for v in all_visits[:10]:
            recent.append({
                'ip': v.ip,
                'ua': v.user_agent,
                'time': v.timestamp.strftime('%H:%M:%S') if v.timestamp else ''
            })

        res = {
            'total_visits': total, 
            'today_visits': today,
            'device_stats': {'mobile': mobile, 'desktop': desktop},
            'recent_visits': recent
        }
        _stats_cache['timestamp'] = now
        _stats_cache['data'] = res
        return res
    except Exception as e:
        print(f"Error getting stats: {e}")
        return _stats_cache['data'] or {'total_visits': 0, 'today_visits': 0, 'device_stats': {'mobile': 0, 'desktop': 0}, 'recent_visits': []}

@main_bp.route('/api/clients', methods=['POST'])
@login_required
def save_client():
    try:
        data = request.json or {}
        client_id = data.get('id')
        if client_id:
            client = Client.query.get(client_id)
            if not client:
                client = Client()
                client.id = client_id
                db.session.add(client)
        else:
            client = Client()
            db.session.add(client)
        
        client.name = data.get('name')
        client.biz = data.get('biz')
        client.phone = data.get('phone')
        client.service = data.get('service')
        client.status = data.get('status')
        client.date = data.get('date')
        
        db.session.commit()
        return jsonify({'success': True, 'id': client.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/clients/<int:id>', methods=['DELETE'])
@login_required
def delete_client(id):
    try:
        client = Client.query.get(id)
        if client:
            db.session.delete(client)
            db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/projects', methods=['POST'])
@login_required
def save_project():
    try:
        data = request.json or {}
        project_id = data.get('id')
        if project_id:
            project = Project.query.get(project_id)
            if not project:
                project = Project()
                project.id = project_id
                db.session.add(project)
        else:
            project = Project()
            db.session.add(project)
        
        project.client = data.get('client')
        project.type = data.get('type')
        project.start = data.get('start')
        project.end = data.get('end')
        project.status = data.get('status')
        project.progress = data.get('progress')
        
        db.session.commit()
        return jsonify({'success': True, 'id': project.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/projects/<int:id>', methods=['DELETE'])
@login_required
def delete_project(id):
    try:
        project = Project.query.get(id)
        if project:
            db.session.delete(project)
            db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/messages', methods=['POST'])
def save_message():
    try:
        data = request.json or {}
        msg_id = data.get('id')
        if msg_id or 'status' in data:
            if not session.get('admin_logged_in'):
                return jsonify({'success': False, 'error': 'No autorizado.'}), 401
            msg = Message.query.get(msg_id)
            if not msg:
                msg = Message()
                if msg_id: msg.id = msg_id
                db.session.add(msg)
            if 'name' in data: msg.name = data.get('name')
            if 'phone' in data: msg.phone = data.get('phone')
            if 'msg' in data: msg.msg = data.get('msg')
            if 'status' in data: msg.status = data.get('status')
        else:
            name = (data.get('name') or '').strip()
            phone = (data.get('phone') or '').strip()
            msg_text = (data.get('msg') or '').strip()
            if not name or not phone:
                return jsonify({'success': False, 'error': 'Nombre y teléfono son obligatorios.'}), 400
            msg = Message(name=name[:100], phone=phone[:20], msg=msg_text[:2000], status='Nuevo')
            db.session.add(msg)
        
        db.session.commit()
        return jsonify({'success': True, 'id': msg.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/messages/<int:id>', methods=['DELETE'])
@login_required
def delete_message(id):
    try:
        msg = Message.query.get(id)
        if msg:
            db.session.delete(msg)
            db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/portfolio', methods=['POST'])
@login_required
def save_portfolio():
    try:
        data = request.json or {}
        p_id = data.get('id')
        if p_id:
            p = PortfolioItem.query.get(p_id)
            if not p:
                p = PortfolioItem()
                p.id = p_id
                db.session.add(p)
        else:
            p = PortfolioItem()
            db.session.add(p)
        
        p.title = data.get('title')
        p.desc = data.get('desc')
        p.url = data.get('url')
        p.link = data.get('link')
        
        db.session.commit()
        return jsonify({'success': True, 'id': p.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/portfolio/<int:id>', methods=['DELETE'])
@login_required
def delete_portfolio(id):
    try:
        p = PortfolioItem.query.get(id)
        if p:
            db.session.delete(p)
            db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/reviews', methods=['POST'])
@login_required
def save_review():
    try:
        data = request.json or {}
        r_id = data.get('id')
        if r_id:
            r = PublicReview.query.get(r_id)
            if not r:
                r = PublicReview()
                r.id = r_id
                db.session.add(r)
        else:
            r = PublicReview()
            db.session.add(r)
        
        r.initials = data.get('initials')
        r.stars = data.get('stars')
        r.name = data.get('name')
        r.biz = data.get('biz')
        r.text = data.get('text')
        
        db.session.commit()
        return jsonify({'success': True, 'id': r.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/reviews/<int:id>', methods=['DELETE'])
@login_required
def delete_review(id):
    try:
        r = PublicReview.query.get(id)
        if r:
            db.session.delete(r)
            db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/visits', methods=['DELETE'])
@login_required
def reset_visits():
    try:
        Visit.query.delete()
        _stats_cache['data'] = None
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/settings', methods=['POST'])
@login_required
def save_settings():
    try:
        data = request.json or {}
        for key, value in data.items():
            setting = Setting.query.get(key)
            if setting:
                setting.value = str(value)
            else:
                setting = Setting()
                setting.key = key
                setting.value = str(value)
                db.session.add(setting)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
