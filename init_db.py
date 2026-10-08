from app import create_app

# create_app() ya crea las tablas y siembra los datos iniciales.
app = create_app()
print("Base de datos inicializada correctamente:", app.config['DATABASE_FILE'])
