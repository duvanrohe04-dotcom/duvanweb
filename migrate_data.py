import os
import sqlite3
from sqlalchemy import create_engine, text
from app import create_app
from extensions import db
from models.models import Client, Project, Message, PortfolioItem, PublicReview, Setting, Visit

def migrate_data():
    # Setup
    app = create_app()
    
    # Paths
    sqlite_path = os.path.join(app.instance_path, 'site.db')
    if not os.path.exists(sqlite_path):
        print(f"No se encontró la base de datos SQLite en: {sqlite_path}")
        return

    # Database URL from environment (Postgres)
    pg_url = os.getenv('DATABASE_URL')
    if not pg_url or 'postgresql' not in pg_url:
        print("DATABASE_URL no está configurada para PostgreSQL.")
        return

    print(f"Migrando datos desde {sqlite_path} hacia PostgreSQL...")

    with app.app_context():
        # Asegurarse de que las tablas existen en Postgres
        db.create_all()
        
        # Conectar a SQLite
        sl_conn = sqlite3.connect(sqlite_path)
        sl_cursor = sl_conn.cursor()

        # Modelos a migrar
        models = [Client, Project, Message, PortfolioItem, PublicReview, Setting, Visit]

        for model in models:
            table_name = model.__tablename__
            print(f"Migrando tabla: {table_name}...")
            
            # Obtener datos de SQLite
            sl_cursor.execute(f"SELECT * FROM {table_name}")
            rows = sl_cursor.fetchall()
            
            if not rows:
                print(f"  Tabla {table_name} vacía. Saltando.")
                continue

            # Obtener nombres de columnas
            columns = [column[0] for column in sl_cursor.description]
            
            # Insertar en Postgres
            # Usamos raw SQL para evitar problemas de sesión con IDs manuales
            placeholders = ", ".join([":" + col for col in columns])
            insert_query = text(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})")
            
            count = 0
            for row in rows:
                data = dict(zip(columns, row))
                try:
                    db.session.execute(insert_query, data)
                    count += 1
                except Exception as e:
                    print(f"  Error insertando fila en {table_name}: {e}")
                    db.session.rollback()
            
            db.session.commit()
            print(f"  Migradas {count} filas a {table_name}.")

        sl_conn.close()
        print("Migración completada exitosamente.")

if __name__ == '__main__':
    migrate_data()
