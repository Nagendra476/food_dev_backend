"""
Django settings for restaurant_backend project.
"""

from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-r0i)3$b&_pun5h$obu8k_xw7a8ve#osvq5qby=ry-rx&w%270q'

DEBUG = False

ALLOWED_HOSTS = ['*']


# ========================
# APPLICATIONS
# ========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',  # ✅ CORS
    'rest_framework.authtoken',
    'api',
]


# ========================
# MIDDLEWARE (FIXED ORDER)
# ========================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # ✅ MUST BE FIRST
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'restaurant_backend.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'restaurant_backend.wsgi.application'


# ========================
# DATABASE
# ========================
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://rest_db_cdyg_user:a8lRp0NmyXGAGHys7gjbv3DtDE5j7ZJY@dpg-d77p1qbuibrs73c4c2ng-a.oregon-postgres.render.com/rest_db_cdyg"
)

if os.environ.get("MYSQLHOST"):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('MYSQLDATABASE'),
            'USER': os.environ.get('MYSQLUSER'),
            'PASSWORD': os.environ.get('MYSQLPASSWORD'),
            'HOST': os.environ.get('MYSQLHOST'),
            'PORT': os.environ.get('MYSQLPORT'),
        }
    }
else:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
        )
    }


# ========================
# PASSWORD VALIDATION
# ========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ========================
# INTERNATIONALIZATION
# ========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


AUTH_USER_MODEL = 'api.User'


# ========================
# STATIC & MEDIA
# ========================
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ========================
# ✅ CORS FIX (IMPORTANT)
# ========================

# Allow your frontend (Vercel)
CORS_ALLOWED_ORIGINS = [
    "https://food-delivery-mbcx.vercel.app",
]

# (optional) allow all (keep for testing)
CORS_ALLOW_ALL_ORIGINS = True

# Allow credentials (for login/auth)
CORS_ALLOW_CREDENTIALS = True

# Allowed headers
CORS_ALLOW_HEADERS = [
    'content-type',
    'authorization',
]

# Allowed methods
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]

# CSRF fix for production (Render + Vercel)
CSRF_TRUSTED_ORIGINS = [
    "https://food-delivery-mbcx.vercel.app",
]


# ========================
# DEFAULT PK
# ========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ========================
# DRF
# ========================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ]
}