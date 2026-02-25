#!/bin/sh
# Wrapper script to start Gunicorn and filter health check logs
# Supports hosted Postgres via DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD (e.g. Railway).

echo '🚀 Starting Django application...'
mkdir -p /app/logs

# When using hosted DB (DB_HOST set): skip nc wait and fix_phone
if [ -n "$DB_HOST" ] && [ "$DB_HOST" != "" ]; then
  echo '✅ Using DB_HOST (Railway/external). Skipping DB wait and fix_phone.'
  echo '🗺️  Ensuring PostGIS extension...'
  python enable_postgis_neon.py || echo '⚠️  PostGIS setup skipped or failed, continuing...'
else
  echo '⏳ Waiting for database connection...'
  until nc -z -v -w30 "${DB_HOST}" "${DB_PORT:-5432}"; do
    echo "Waiting for database at ${DB_HOST}:${DB_PORT:-5432}..."
    sleep 2
  done
  echo '✅ Database is up and running!'
  echo '🔧 Fixing phone number issues before migrations...'
  python fix_phone_before_migrations.py || echo '⚠️  Phone fix script failed, continuing...'
fi

echo '📊 Applying database migrations...'
python manage.py migrate --noinput

echo '📁 Collecting static files...'
python manage.py collectstatic --noinput

echo '🌐 Starting Gunicorn server (health checks filtered from logs)...'

# PORT: Fly.io uses 8080, Render uses PORT from env, local default 8000
PORT=${PORT:-8000}
exec gunicorn farm_management.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    2>&1 | python3 /app/filter_health_checks.py

