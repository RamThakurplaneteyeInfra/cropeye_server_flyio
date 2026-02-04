"""
WSGI config for farm_management project.
"""

import os

from django.core.wsgi import get_wsgi_application

# Use production settings (Neon DB) when DATABASE_URL is set; otherwise development
_db_url = os.environ.get('DATABASE_URL', '')
if _db_url and _db_url.strip().startswith('postgresql'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_management.settings_production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_management.settings')

application = get_wsgi_application() 