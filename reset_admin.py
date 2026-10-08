"""Restablece el acceso del admin a: usuario `admin` / contraseña `admin123`.

Uso:  python reset_admin.py
En Coolify (terminal del contenedor): python reset_admin.py
"""
from werkzeug.security import generate_password_hash

from app import create_app
from extensions import db
from models.models import Setting
from seed import DEFAULT_ADMIN_PASSWORD

app = create_app()
with app.app_context():
    row = db.session.get(Setting, 'dr_admin_pass') or Setting(key='dr_admin_pass')
    row.value = generate_password_hash(DEFAULT_ADMIN_PASSWORD)
    db.session.add(row)
    db.session.commit()
    print(f"Listo -> usuario: admin | contraseña: {DEFAULT_ADMIN_PASSWORD} ({app.config['DATABASE_FILE']})")
