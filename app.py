import os
from flask import Flask, send_from_directory
from dotenv import load_dotenv

load_dotenv()

from conf.settings import get_config
from routes.main import main_bp
from extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    db.init_app(app)
    
    with app.app_context():
        from models.models import Setting, PublicReview, Client, Project, Message, PortfolioItem, Visit
        try:
            db.create_all()
            # Seed initial data if empty
            if not Setting.query.get('dr_wa'):
                db.session.add(Setting(key='dr_wa', value='3107480575'))
                db.session.add(Setting(key='dr_tagline', value='Tu pagina web profesional lista en solo dias'))
                db.session.add(Setting(key='dr_footer_1', value=''))
                db.session.add(Setting(key='dr_footer_2', value=''))
                db.session.add(Setting(key='dr_social_ig', value=''))
                db.session.add(Setting(key='dr_social_tt', value=''))
                db.session.add(Setting(key='dr_admin_pass', value='DR2026admin'))
                db.session.add(Setting(key='dr_income', value='0'))
                db.session.commit()
        except Exception as e:
            print(f"DB Init info (can be ignored if running multiple workers): {e}")
            db.session.rollback()
        if not PublicReview.query.first():
            reviews = [
                PublicReview(initials='MC', stars=5, name='María Camila Torres', biz='🍽️ Restaurante El Fogón — Bogotá', text='Desde que Duvan me hizo la página, mis reservas se duplicaron. Ahora recibo clientes de toda Bogotá y hasta de otras ciudades. La inversión se pagó sola en el primer mes.'),
                PublicReview(initials='JA', stars=5, name='Juan Andrés Mejía', biz='✂️ Barbería Style — Medellín', text='Mi peluquería ahora aparece en Google cuando la gente busca cortes de cabello cerca. Antes dependía solo del voz a voz. Duvan hizo un trabajo muy profesional y rápido.'),
                PublicReview(initials='LP', stars=5, name='Laura Patricia Gómez', biz='👗 Boutique LPG — Cali', text='Tengo mi tienda en línea funcionando perfectamente. Vendo a todo el país sin salir de mi casa. El panel es fácil de usar y Duvan siempre responde cuando lo necesito.')
            ]
            db.session.bulk_save_objects(reviews)
        db.session.commit()

    app.register_blueprint(main_bp)

    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    @app.route('/sw.js')
    def service_worker():
        resp = send_from_directory('static', 'sw.js', mimetype='application/javascript')
        resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        resp.headers['Pragma'] = 'no-cache'
        return resp

    @app.route('/manifest.webmanifest')
    def manifest():
        return send_from_directory('static', 'manifest.webmanifest', mimetype='application/manifest+json')

    return app
