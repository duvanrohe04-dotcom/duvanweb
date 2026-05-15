from flask import Blueprint, render_template, request, jsonify
from extensions import db
from models.models import Client, Project, Message, PortfolioItem, PublicReview, Setting, Visit
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    try:
        visit = Visit()
        visit.ip = request.remote_addr
        visit.user_agent = request.headers.get('User-Agent')
        db.session.add(visit)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error recording visit: {e}")
    return render_template('index.html')

# --- API ROUTES ---

@main_bp.route('/api/init', methods=['GET'])
def get_init_data():
    clients = Client.query.all()
    projects = Project.query.all()
    messages = Message.query.all()
    portfolio = PortfolioItem.query.all()
    reviews = PublicReview.query.all()
    settings = Setting.query.all()
    
    settings_dict = {s.key: s.value for s in settings}
    
    # Visit Stats
    stats = get_stats()
    
    return jsonify({
        'clients': [{ 'id': c.id, 'name': c.name, 'biz': c.biz, 'phone': c.phone, 'service': c.service, 'status': c.status, 'date': c.date } for c in clients],
        'projects': [{ 'id': p.id, 'client': p.client, 'type': p.type, 'start': p.start, 'end': p.end, 'status': p.status, 'progress': p.progress } for p in projects],
        'messages': [{ 'id': m.id, 'name': m.name, 'phone': m.phone, 'msg': m.msg, 'status': m.status } for m in messages],
        'portfolio': [{ 'id': p.id, 'title': p.title, 'desc': p.desc, 'url': p.url, 'link': p.link } for p in portfolio],
        'reviews': [{ 'id': r.id, 'initials': r.initials, 'stars': r.stars, 'name': r.name, 'biz': r.biz, 'text': r.text } for r in reviews],
        'settings': settings_dict,
        'stats': stats
    })

def get_stats():
    try:
        total = Visit.query.count()
        # Colombia is UTC-5
        from datetime import timedelta
        now_col = datetime.utcnow() - timedelta(hours=5)
        today_start_col = now_col.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # We compare stored UTC timestamps with the calculated UTC equivalent of Colombia's midnight
        # Colombia 00:00 is UTC 05:00
        today_start_utc = today_start_col + timedelta(hours=5)
        today = Visit.query.filter(Visit.timestamp >= today_start_utc).count()
        
        # Breakdown by device (last 100 visits)
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
                'time': v.timestamp.strftime('%H:%M:%S')
            })

        return {
            'total_visits': total, 
            'today_visits': today,
            'device_stats': {'mobile': mobile, 'desktop': desktop},
            'recent_visits': recent
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {'total_visits': 0, 'today_visits': 0, 'device_stats': {'mobile': 0, 'desktop': 0}, 'recent_visits': []}

@main_bp.route('/api/clients', methods=['POST'])
def save_client():
    data = request.json
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

@main_bp.route('/api/clients/<int:id>', methods=['DELETE'])
def delete_client(id):
    client = Client.query.get(id)
    if client:
        db.session.delete(client)
        db.session.commit()
    return jsonify({'success': True})

@main_bp.route('/api/projects', methods=['POST'])
def save_project():
    data = request.json
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

@main_bp.route('/api/projects/<int:id>', methods=['DELETE'])
def delete_project(id):
    project = Project.query.get(id)
    if project:
        db.session.delete(project)
        db.session.commit()
    return jsonify({'success': True})

@main_bp.route('/api/messages', methods=['POST'])
def save_message():
    data = request.json
    msg_id = data.get('id')
    if msg_id:
        msg = Message.query.get(msg_id)
        if not msg:
            msg = Message()
            msg.id = msg_id
            db.session.add(msg)
    else:
        msg = Message()
        db.session.add(msg)
    
    msg.name = data.get('name')
    msg.phone = data.get('phone')
    msg.msg = data.get('msg')
    msg.status = data.get('status')
    
    db.session.commit()
    return jsonify({'success': True, 'id': msg.id})

@main_bp.route('/api/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    msg = Message.query.get(id)
    if msg:
        db.session.delete(msg)
        db.session.commit()
    return jsonify({'success': True})

@main_bp.route('/api/portfolio', methods=['POST'])
def save_portfolio():
    data = request.json
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

@main_bp.route('/api/portfolio/<int:id>', methods=['DELETE'])
def delete_portfolio(id):
    p = PortfolioItem.query.get(id)
    if p:
        db.session.delete(p)
        db.session.commit()
    return jsonify({'success': True})

@main_bp.route('/api/reviews', methods=['POST'])
def save_review():
    data = request.json
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

@main_bp.route('/api/reviews/<int:id>', methods=['DELETE'])
def delete_review(id):
    r = PublicReview.query.get(id)
    if r:
        db.session.delete(r)
        db.session.commit()
    return jsonify({'success': True})

@main_bp.route('/api/visits', methods=['DELETE'])
def reset_visits():
    try:
        Visit.query.delete()
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@main_bp.route('/api/settings', methods=['POST'])
def save_settings():
    data = request.json
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
