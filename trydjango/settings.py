from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',        # ← enables session framework
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',                           # ← register your app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',   # ← session support
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',              # ← CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.RequestLoggingMiddleware',   # ← custom: logs every request
    'core.middleware.CustomErrorMiddleware',      # ← custom: handles exceptions
]

ROOT_URLCONF = 'trydjango.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,   # ← looks for templates in core/templates/
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'trydjango.wsgi.application'

# ── Relational Database (SQLite) ──────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ── Session Configuration ─────────────────────────────────────────
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # store sessions in DB
SESSION_COOKIE_AGE = 3600        # expire after 1 hour
SESSION_COOKIE_HTTPONLY = True   # JS cannot read the cookie
SESSION_COOKIE_SECURE = False    # set True in production (HTTPS)
SESSION_SAVE_EVERY_REQUEST = True

# ── Auth Redirects ────────────────────────────────────────────────
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# ── Logging middleware output ─────────────────────────────────────
LOG_FILE = BASE_DIR / 'requests.log'

STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'