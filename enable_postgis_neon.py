"""
Enable PostGIS extension on Railway Postgres (or any PostgreSQL) before running migrations.
Uses DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD from environment (same as Django).

Usage: python enable_postgis_neon.py
"""
import os
import sys
from pathlib import Path

# Load .env from project root (same as Django)
project_root = Path(__file__).resolve().parent
if (project_root / '.env.local').exists():
    from dotenv import load_dotenv
    load_dotenv(project_root / '.env.local')
elif (project_root / '.env').exists():
    from dotenv import load_dotenv
    load_dotenv(project_root / '.env')

import psycopg2


def main():
    host = (os.environ.get('DB_HOST') or '').strip()
    if not host:
        print('DB_HOST not set. Skipping PostGIS setup.')
        return 0
    dbname = (os.environ.get('DB_NAME') or '').strip() or 'railway'
    port = (os.environ.get('DB_PORT') or '').strip() or '5432'
    user = (os.environ.get('DB_USER') or '').strip() or 'postgres'
    password = os.environ.get('DB_PASSWORD') or ''

    print('Enabling PostGIS extension on database...')
    try:
        conn = psycopg2.connect(
            host=host,
            port=int(port),
            dbname=dbname[:63],
            user=user,
            password=password,
            sslmode='require',
            connect_timeout=10,
        )
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute('CREATE EXTENSION IF NOT EXISTS postgis;')
        conn.close()
        print('PostGIS extension enabled.')
        return 0
    except psycopg2.Error as e:
        print(f'Error enabling PostGIS: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
