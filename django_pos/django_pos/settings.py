"""
Django settings for django_pos project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ============================================================
# PATH CONFIGURATION
# BASE_DIR  — root of the project (where manage.py lives)
# CORE_DIR  — same as BASE_DIR but resolved via os.path (legacy compat)
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file into os.environ
# This must run before any os.environ.get() calls below
load_dotenv()


# ============================================================
# SECURITY SETTINGS
# SECRET_KEY — cryptographic signing key; never hardcode or commit
# DEBUG      — enables verbose error pages; must be False in production
# ============================================================
SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Hosts/domains this Django site is allowed to serve
# Empty in development; add your domain in production e.g. ['mysite.com']
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')


# ============================================================
# APPLICATION DEFINITION
# DJANGO_APPS — built-in Django modules (auth, admin, sessions, etc.)
# LOCAL_APPS  — your own Django apps (the business logic modules)
# INSTALLED_APPS — the merged list Django reads at startup
# ============================================================
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

LOCAL_APPS = [
    "pos",
    "products",
    "sales",
    "customers",
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS


# ============================================================
# MIDDLEWARE
# Middleware is a request/response processing pipeline.
# Each middleware layer wraps the view — think of it as
# a series of hooks that run on every HTTP request and response.
# ============================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",        # CSRF — Cross-Site Request Forgery protection
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================================================
# URL & AUTHENTICATION ROUTING
# ROOT_URLCONF       — the master URL dispatcher module
# LOGIN_URL          — redirects unauthenticated users here
# LOGIN_REDIRECT_URL — where to go after a successful login
# LOGOUT_REDIRECT_URL— where to go after logout
# ============================================================
ROOT_URLCONF = "django_pos.urls"
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = "authentication:home"
LOGOUT_REDIRECT_URL = "authentication:login"


# ============================================================
# TEMPLATES
# Django's templating engine config.
# TEMPLATE_DIR — filesystem path where shared templates live
# APP_DIRS     — also look for templates inside each app's /templates/ folder
# context_processors — inject common variables into every template context
# ============================================================
TEMPLATE_DIR = os.path.join(CORE_DIR, "templates")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI — Web Server Gateway Interface
# The entrypoint that connects Django to a web server (e.g. Gunicorn, Apache)
WSGI_APPLICATION = "django_pos.wsgi.application"


# ============================================================
# DATABASE CONFIGURATION
# Environment-driven — switch between SQLite and MySQL via .env
# ENGINE  — the database backend/driver Django uses
# NAME    — database name (or file path for SQLite)
# USER, PASSWORD, HOST, PORT — connection credentials (MySQL/Postgres only)
#

# ============================================================
DATABASES = {
    "default": {
        "ENGINE"  : os.environ.get("DB_ENGINE",   "mssql"),
        "NAME"    : os.environ.get("DB_NAME",      "pos_db"),
        "USER"    : os.environ.get("DB_USER",      "pos_user"),
        "PASSWORD": os.environ.get("DB_PASSWORD",  ""),
        "HOST"    : os.environ.get("DB_HOST",      "Streak"),
        "PORT"    : os.environ.get("DB_PORT",      "1433"),
        "OPTIONS" : {
            # ODBC Driver 18 is what you have installed
            "driver"              : "ODBC Driver 18 for SQL Server",
            # Trust the self-signed cert — required for local dev
            "extra_params": "TrustServerCertificate=yes;Encrypt=no;",
            # autocommit required for Django DDL statements in T-SQL
            "autocommit"          : True,
        },
    }
}


# ============================================================
# PASSWORD VALIDATION
# A pipeline of validators Django runs when a user sets a password.
# Each validator enforces a different security rule.
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    # Rejects passwords too similar to the user's username/email
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    # Enforces a minimum character length
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    # Rejects commonly used passwords (e.g. "password123")
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    # Rejects entirely numeric passwords
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ============================================================
# INTERNATIONALISATION (i18n) & LOCALISATION (l10n)
# LANGUAGE_CODE — default language for the project
# TIME_ZONE     — all datetime objects stored/displayed in this zone
# USE_I18N      — enables Django's translation framework
# USE_TZ        — makes Django timezone-aware (recommended: True)
# ============================================================
LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Nairobi"   # EAT — East Africa Time (UTC+3)

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC FILES
# Static files = CSS, JavaScript, images shipped with the app.
# STATIC_URL      — the URL prefix browsers use to request static files
# STATIC_ROOT     — where `collectstatic` gathers all static files for deployment
# STATICFILES_DIRS— additional directories Django scans for static files in dev
# ============================================================
STATIC_ROOT = os.path.join(CORE_DIR, 'staticfiles')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(CORE_DIR, 'static'),
)


# ============================================================
# DEFAULT PRIMARY KEY
# BigAutoField — auto-incrementing 64-bit integer PK for all models
# without an explicitly defined primary key
# ============================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"