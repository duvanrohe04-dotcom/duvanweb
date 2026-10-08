import os
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from extensions import db
from models.models import Setting, PublicReview

DEFAULT_ADMIN_PASSWORD = 'admin123'
RESET_MARKER = 'admin_creds_reset_v2'

DEFAULT_SETTINGS = {
    'dr_wa': '3107480575',
    'dr_tagline': 'Tu pagina web profesional lista en solo dias',
    'dr_footer_1': '',
    'dr_footer_2': '',
    'dr_social_ig': '',
    'dr_social_tt': '',
    'dr_income': '0',
}

DEFAULT_REVIEWS = [
    dict(initials='MC', stars=5, name='María Camila Torres', biz='🍽️ Restaurante El Fogón — Bogotá',
         text='Desde que Duvan me hizo la página, mis reservas se duplicaron. Ahora recibo clientes de toda Bogotá y hasta de otras ciudades. La inversión se pagó sola en el primer mes.'),
    dict(initials='JA', stars=5, name='Juan Andrés Mejía', biz='✂️ Barbería Style — Medellín',
         text='Mi peluquería ahora aparece en Google cuando la gente busca cortes de cabello cerca. Antes dependía solo del voz a voz. Duvan hizo un trabajo muy profesional y rápido.'),
    dict(initials='LP', stars=5, name='Laura Patricia Gómez', biz='👗 Boutique LPG — Cali',
         text='Tengo mi tienda en línea funcionando perfectamente. Vendo a todo el país sin salir de mi casa. El panel es fácil de usar y Duvan siempre responde cuando lo necesito.'),
]


def seed_defaults():
    """Crea tablas y datos iniciales. Idempotente y tolerante a carreras entre workers."""
    db.create_all()
    try:
        for key, value in DEFAULT_SETTINGS.items():
            if db.session.get(Setting, key) is None:
                db.session.add(Setting(key=key, value=value))
        pw = db.session.get(Setting, 'dr_admin_pass')
        if pw is None:
            pw = Setting(key='dr_admin_pass')
            db.session.add(pw)
            pw.value = generate_password_hash(os.getenv('ADMIN_PASSWORD') or DEFAULT_ADMIN_PASSWORD)
            db.session.add(Setting(key=RESET_MARKER, value='1'))
        elif db.session.get(Setting, RESET_MARKER) is None:
            # Reinicio único de credenciales: usuario admin / contraseña admin123.
            pw.value = generate_password_hash(DEFAULT_ADMIN_PASSWORD)
            db.session.add(Setting(key=RESET_MARKER, value='1'))
        if PublicReview.query.first() is None:
            db.session.add_all([PublicReview(**r) for r in DEFAULT_REVIEWS])
        db.session.commit()
    except IntegrityError:
        # Otro worker sembró al mismo tiempo.
        db.session.rollback()
