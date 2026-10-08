import os
from flask import Flask, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

load_dotenv()

from conf.settings import get_config
from extensions import db


def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config_object or get_config())

    # Detrás de Traefik/Coolify: confiar en un salto de X-Forwarded-*.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(os.path.dirname(app.config['DATABASE_FILE']), exist_ok=True)

    db.init_app(app)

    from routes.main import main_bp
    from seed import seed_defaults

    with app.app_context():
        from models import models  # noqa: F401  (registra las tablas)
        seed_defaults()

    app.register_blueprint(main_bp)

    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    @app.route('/health')
    def health():
        return {'status': 'ok'}

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
