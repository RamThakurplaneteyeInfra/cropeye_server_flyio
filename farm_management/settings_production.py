import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Load .env from project root so DB_HOST, DB_NAME, etc. are set when running in Docker
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'


# ALLOWED_HOSTS - Use '*' in production (Render/Fly reverse-proxy deployments)
# Render and Fly terminate TLS and forward Host; exact hostnames vary. Restricting
# causes DisallowedHost. Restrict via ALLOWED_HOSTS env only if you run without a proxy.
_render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
# Railway injects the service’s public hostname (e.g. app.up.railway.app); required for CSRF on admin/forms.
_railway_public_domain = (os.environ.get('RAILWAY_PUBLIC_DOMAIN') or '').strip()
fly_app = os.environ.get('FLY_APP_NAME', 'cropeye-server')
allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', '').strip()
if allowed_hosts_env and allowed_hosts_env != '*':
    ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(',') if h.strip()]
    ALLOWED_HOSTS = [h for h in ALLOWED_HOSTS if not h.startswith('*')]
    for domain in (
        'cropeye-server-1.onrender.com', 'cropeye-server.onrender.com',
        'cropeye-server-flyio.onrender.com', 'farm-management-web.onrender.com',
        f'{fly_app}.fly.dev', '.fly.dev', 'localhost', '127.0.0.1',
    ):
        if domain not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(domain)
    if _render_host and _render_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_render_host)
    if _railway_public_domain and _railway_public_domain not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_railway_public_domain)
else:
    ALLOWED_HOSTS = ['*']

# CSRF trusted origins (required for Django 4.1+ with cross-origin form POSTs)
csrf_origins = [
    f'https://{fly_app}.fly.dev',
    'https://cropeye-server-1.onrender.com',
    'https://cropeye-server.onrender.com',
    'https://cropeye-server-flyio.onrender.com',
    'https://farm-management-web.onrender.com',
    'https://farm-management-web-production-c3ca.up.railway.app',
]
if _railway_public_domain:
    _railway_origin = _railway_public_domain.rstrip('/')
    if not _railway_origin.startswith(('http://', 'https://')):
        _railway_origin = f'https://{_railway_origin}'
    csrf_origins.append(_railway_origin)
if _render_host:
    csrf_origins.append(f'https://{_render_host}')
_csrf_env = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if _csrf_env:
    csrf_origins.extend(o.strip() for o in _csrf_env.split(',') if o.strip())
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(csrf_origins))

# Railway / Render / Fly terminate TLS and forward HTTP. Without this, request.is_secure()
# and get_host() are wrong, so CSRF compares Origin to http://internal:port and fails.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',  # Enable GeoDjango
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    'django_filters',
    'leaflet',
    'django_prometheus',
    
    # Local apps
    'users',
    'tasks',
    'equipment',
    'bookings',
    'inventory',
    'vendors',
    'farms',
    'messaging',  # Two-way communication system
    'chatbot',
    'industries',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'farm_management.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'farm_management.wsgi.application'

# Database - explicit DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD only (no DATABASE_URL, no localhost fallback)
_db_host = (os.environ.get('DB_HOST') or '').strip()
if not _db_host:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured(
        'DB_HOST is required in production. Set DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD in .env (e.g. Railway).'
    )

_db_sslmode = (os.environ.get('DB_SSLMODE') or '').strip()
_db_options = {'sslmode': _db_sslmode} if _db_sslmode else {}

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': (os.environ.get('DB_NAME') or '').strip() or 'railway',
        'USER': (os.environ.get('DB_USER') or '').strip() or 'postgres',
        'PASSWORD': (os.environ.get('DB_PASSWORD') or ''),
        'HOST': _db_host,
        'PORT': (os.environ.get('DB_PORT') or '').strip() or '5432',
        'OPTIONS': _db_options,
        'DISABLE_SERVER_SIDE_CURSORS': True,
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
_static_project = BASE_DIR / 'static'
STATICFILES_DIRS = [_static_project] if _static_project.is_dir() else []

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'users.User'

# Custom authentication backend for phone number login
AUTHENTICATION_BACKENDS = [
    'users.backends.PhoneNumberBackend',  # Phone number authentication
    'django.contrib.auth.backends.ModelBackend',  # Fallback to default
]

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS settings - Allow all origins for development and flexibility
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Swagger settings – tag all modules (Users, Farms, Equipment, etc.) so they appear in UI
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'DEFAULT_AUTO_SCHEMA_CLASS': 'farm_management.swagger_schema.TaggedSwaggerAutoSchema',
}

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', '')

# Mailgun Configuration for OTP emails
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY', '')
MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN', '')
MAILGUN_FROM_EMAIL = os.environ.get('MAILGUN_FROM_EMAIL', DEFAULT_FROM_EMAIL)

# Frontend URL for password reset links
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

# LEAFLET_CONFIG 
LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (28.6139, 77.2090),  # Coordinates for New Delhi, India
    'DEFAULT_ZOOM': 6,
    'MIN_ZOOM': 3,
    'MAX_ZOOM': 18,
    'RESET_VIEW': True,
    'TILES': 'http://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
    'ATTRIBUTION': '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}

# FastAPI Services URLs (Public tunnel URLs for hosted Django to sync with local FastAPI)
EVENTS_API_URL = os.environ.get('EVENTS_API_URL', 'https://dev-events.cropeye.ai')
SOIL_API_URL = os.environ.get('SOIL_API_URL', 'https://dev-soil.cropeye.ai')
ADMIN_API_URL = os.environ.get('ADMIN_API_URL', 'https://dev-plot.cropeye.ai')
FIELD_API_URL = os.environ.get('FIELD_API_URL', 'https://dev-field.cropeye.ai')

# FastAPI Authentication Credentials
ADMIN_API_USERNAME = os.environ.get('ADMIN_API_USERNAME', 'devuser')
ADMIN_API_PASSWORD = os.environ.get('ADMIN_API_PASSWORD', 'KGZvvyd*9k')
FIELD_API_USERNAME = os.environ.get('FIELD_API_USERNAME', 'devuser')
FIELD_API_PASSWORD = os.environ.get('FIELD_API_PASSWORD', 'KGZvvyd*9k')

# WhatsApp OTP Configuration (Twilio)
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER', '')

# OTP Configuration
WHATSAPP_OTP_ENABLED = os.environ.get('WHATSAPP_OTP_ENABLED', 'True').lower() == 'true'
EMAIL_OTP_FALLBACK = os.environ.get('EMAIL_OTP_FALLBACK', 'True').lower() == 'true'

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session security
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Cache configuration (Redis recommended for production; use dummy on Fly.io if no Redis)
_redis_url = os.environ.get('REDIS_URL', '').strip()
if _redis_url:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': _redis_url,
        }
    }
    # Store sessions in Redis to reduce DB load on every request (avoids DB hit per request)
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

# Celery configuration (if using background tasks)
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')