# Deploy CropEye Django API on Fly.io

This project is configured to run on [Fly.io](https://fly.io) with **Neon PostgreSQL** (external DB). The app uses GeoDjango (PostGIS), Gunicorn, and WhiteNoise.

## Prerequisites

- [Fly CLI](https://fly.io/docs/hands-on/install-flyctl/) installed and logged in (`fly auth login`)
- Neon database with PostGIS enabled (see `enable_postgis_neon.py`)
- Migrations applied to Neon (or they will run at deploy via `release_command`)

## 1. Create the app (first time only)

From the project root:

```bash
fly launch --no-deploy
```

- **App name**: Use `cropeye-server` or choose another (must match `app` in `fly.toml` if you edit it).
- **Region**: e.g. `sin` (Singapore) if using Neon in `ap-southeast-1`.
- **Postgres**: **No** (we use Neon).
- **Redis**: **No** (optional; app uses DummyCache if no `REDIS_URL`).

This creates the app and `fly.toml`. The repo already includes a `fly.toml`; `fly launch` may overwrite it. If so, restore `fly.toml` from git or re-add:

- `[env]` with `PORT`, `DJANGO_SETTINGS_MODULE`
- `[http_service]` with `internal_port = 8080`, health check `path = "/api/health/"`
- `[deploy]` with `release_command` and `release_command_timeout`
- `[[vm]]` with `memory = "1gb"`

## 2. Set secrets

Set **at least** these secrets (required for Neon + Django):

```bash
fly secrets set SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
fly secrets set DATABASE_URL="postgresql://USER:PASSWORD@HOST/DB?sslmode=require"
```

Replace `DATABASE_URL` with your **Neon** connection string (pooler URL with `?sslmode=require`).

Optional:

```bash
fly secrets set DEBUG="False"
fly secrets set ALLOWED_HOSTS="cropeye-server.fly.dev"
# If using Redis:
fly secrets set REDIS_URL="redis://..."
# Twilio / Mailgun / etc.
fly secrets set TWILIO_ACCOUNT_SID="..." TWILIO_AUTH_TOKEN="..." TWILIO_WHATSAPP_NUMBER="..."
```

## 3. Deploy

```bash
fly deploy
```

This will:

1. Build the Docker image (uses `Dockerfile`).
2. Run `release_command`: `enable_postgis_neon.py` then `manage.py migrate --noinput`.
3. Start machines; app listens on `PORT` (8080) and serves `/api/health/` for Fly health checks.

## 4. Open the app

```bash
fly open
```

Or visit `https://<your-app-name>.fly.dev`. Check:

- `https://<your-app-name>.fly.dev/api/health/`
- `https://<your-app-name>.fly.dev/swagger/`
- `https://<your-app-name>.fly.dev/admin/`

## Useful commands

| Task | Command |
|------|---------|
| Deploy | `fly deploy` |
| Logs | `fly logs` |
| SSH console | `fly ssh console` |
| Django shell | `fly ssh console` then `python manage.py shell` |
| Create superuser | `fly ssh console --pty -C "python manage.py createsuperuser"` |
| Secrets | `fly secrets list`, `fly secrets set K=V` |
| Scale | `fly scale count 1`, `fly scale vm shared-cpu-1x` |

## Environment overview

- **`PORT`**: Set to `8080` in `fly.toml`; app binds to `0.0.0.0:PORT`.
- **`DATABASE_URL`**: Neon PostgreSQL URL; required. PostGIS must be enabled on the DB.
- **`SECRET_KEY`**: Required; set via `fly secrets set`.
- **`FLY_APP_NAME`**: Set by Fly; used for `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` (see `settings_production`).

## Troubleshooting

- **Deploy fails on `release_command`**: Ensure `DATABASE_URL` is set and Neon has PostGIS. Run `enable_postgis_neon.py` once manually if needed.
- **502 / unhealthy**: Check `fly logs`. Confirm app listens on `8080` and `/api/health/` returns 200.
- **CSRF / 403 on form POST**: Add your frontend origin to `CSRF_TRUSTED_ORIGINS` (env or `settings_production`), including `https://<app>.fly.dev` if needed.

## Custom domain

See [Fly custom domains](https://fly.io/docs/app-guides/custom-domains/). After adding a domain, add it to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` (e.g. via env or `settings_production`).
