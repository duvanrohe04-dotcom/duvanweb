import os
from flask import Flask, send_from_directory
from dotenv import load_dotenv

load_dotenv()

from conf.settings import get_config
from routes.main import main_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dr-web-change-me-in-production')

    app.register_blueprint(main_bp)

    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    @app.route('/sw.js')
    def service_worker():
        return send_from_directory('static', 'sw.js', mimetype='application/javascript')

    @app.route('/manifest.webmanifest')
    def manifest():
        return send_from_directory('static', 'manifest.webmanifest', mimetype='application/manifest+json')

    return app
