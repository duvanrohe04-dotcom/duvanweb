from app import create_app
from extensions import db
from models.models import Client, Project, Message, PortfolioItem, PublicReview, Setting, Visit

app = create_app()

with app.app_context():
    db.create_all()
    print("Base de datos inicializada correctamente.")
    
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
        
    if not PublicReview.query.first():
        reviews = [
            PublicReview(initials='MC', stars=5, name='María Camila Torres', biz='🍽️ Restaurante El Fogón — Bogotá', text='Desde que Duvan me hizo la página, mis reservas se duplicaron. Ahora recibo clientes de toda Bogotá y hasta de otras ciudades. La inversión se pagó sola en el primer mes.'),
            PublicReview(initials='JA', stars=5, name='Juan Andrés Mejía', biz='✂️ Barbería Style — Medellín', text='Mi peluquería ahora aparece en Google cuando la gente busca cortes de cabello cerca. Antes dependía solo del voz a voz. Duvan hizo un trabajo muy profesional y rápido.'),
            PublicReview(initials='LP', stars=5, name='Laura Patricia Gómez', biz='👗 Boutique LPG — Cali', text='Tengo mi tienda en línea funcionando perfectamente. Vendo a todo el país sin salir de mi casa. El panel es fácil de usar y Duvan siempre responde cuando lo necesito.')
        ]
        db.session.bulk_save_objects(reviews)
        
    db.session.commit()
    print("Datos iniciales sembrados.")
