"""
WSGI config for farm_management project.
"""

import os

from django.core.wsgi import get_wsgi_application

# Use production settings when DB_HOST is set (hosted DB); otherwise development
_db_host = (os.environ.get('DB_HOST') or '').strip()
if _db_host:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_management.settings_production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_management.settings')

application = get_wsgi_application() 