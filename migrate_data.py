"""Migración única de datos: PostgreSQL (Coolify, antiguo) -> SQLite.

Uso (requiere `pip install psycopg2-binary` SOLO para correr este script):

    python migrate_data.py --pg-url postgresql+psycopg2://USER:PASS@HOST:5432/DB [--sqlite /ruta/duvan_web.db]

Reemplaza el contenido de las tablas en el SQLite destino.
"""
import argparse
import os

from sqlalchemy import create_engine, text, inspect

TABLES = ['client', 'project', 'message', 'portfolio_item', 'public_review', 'setting', 'visit']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pg-url', required=True)
    ap.add_argument('--sqlite', default=None, help='Ruta destino (por defecto DATABASE_PATH o instance/duvan_web.db)')
    args = ap.parse_args()

    if args.sqlite:
        os.environ['DATABASE_PATH'] = args.sqlite

    from app import create_app
    app = create_app()
    dest = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    src = create_engine(args.pg_url)
    src_tables = set(inspect(src).get_table_names())

    with src.connect() as s, dest.begin() as d:
        for table in TABLES:
            if table not in src_tables:
                print(f'- {table}: no existe en Postgres, se omite')
                continue
            rows = s.execute(text(f'SELECT * FROM {table}')).mappings().all()
            d.execute(text(f'DELETE FROM {table}'))
            if rows:
                cols = list(rows[0].keys())
                d.execute(
                    text(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(':' + c for c in cols)})"),
                    [dict(r) for r in rows],
                )
            print(f'- {table}: {len(rows)} filas')
    print('Listo ->', app.config['DATABASE_FILE'])


if __name__ == '__main__':
    main()
