from flask import Blueprint, render_template, request, jsonify
from extensions import db
from models.models import Client, Project, Message, PortfolioItem, PublicReview, Setting

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
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
    
    return jsonify({
        'clients': [{ 'id': c.id, 'name': c.name, 'biz': c.biz, 'phone': c.phone, 'service': c.service, 'status': c.status, 'date': c.date } for c in clients],
        'projects': [{ 'id': p.id, 'client': p.client, 'type': p.type, 'start': p.start, 'end': p.end, 'status': p.status, 'progress': p.progress } for p in projects],
        'messages': [{ 'id': m.id, 'name': m.name, 'phone': m.phone, 'msg': m.msg, 'status': m.status } for m in messages],
        'portfolio': [{ 'id': p.id, 'title': p.title, 'desc': p.desc, 'url': p.url, 'link': p.link } for p in portfolio],
        'reviews': [{ 'id': r.id, 'initials': r.initials, 'stars': r.stars, 'name': r.name, 'biz': r.biz, 'text': r.text } for r in reviews],
        'settings': settings_dict
    })

@main_bp.route('/api/clients', methods=['POST'])
def save_client():
    data = request.json
    client_id = data.get('id')
    if client_id:
        client = Client.query.get(client_id)
        if not client:
            client = Client(id=client_id)
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
            project = Project(id=project_id)
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
            msg = Message(id=msg_id)
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
            p = PortfolioItem(id=p_id)
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
            r = PublicReview(id=r_id)
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

@main_bp.route('/api/settings', methods=['POST'])
def save_settings():
    data = request.json
    for key, value in data.items():
        setting = Setting.query.get(key)
        if setting:
            setting.value = str(value)
        else:
            setting = Setting(key=key, value=str(value))
            db.session.add(setting)
    db.session.commit()
    return jsonify({'success': True})
