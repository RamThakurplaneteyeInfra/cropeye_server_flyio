#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Use production settings (Neon DB) when DATABASE_URL is set; otherwise development
    _db_url = os.environ.get('DATABASE_URL', '')
    if _db_url and _db_url.strip().startswith('postgresql'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_management.settings_production')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_management.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main() 