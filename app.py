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
