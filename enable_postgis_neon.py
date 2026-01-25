"""
Enable PostGIS extension on Neon (or any PostgreSQL) before running migrations.
Run once before `python manage.py migrate` when using a fresh Neon database.

Usage: python enable_postgis_neon.py
"""
import os
import sys

# Load .env so DATABASE_URL is available
from pathlib import Path
path = Path(__file__).resolve().parent
if (path / '.env.local').exists():
    from dotenv import load_dotenv
    load_dotenv(path / '.env.local')
elif (path / '.env').exists():
    from dotenv import load_dotenv
    load_dotenv(path / '.env')

import psycopg2


def main():
    url = os.environ.get('DATABASE_URL')
    if not url or not url.startswith('postgresql'):
        print('DATABASE_URL (postgresql://...) not set in environment. Skipping PostGIS setup.')
        return 0

    print('Enabling PostGIS extension on database...')
    try:
        conn = psycopg2.connect(url)
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
