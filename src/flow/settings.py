# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import environ
from corsheaders.defaults import default_headers

# Deployment configurations
ROOT_DIR = environ.Path(__file__) - 3
APPS_DIR = ROOT_DIR.path('src')
ENV_PATH = str(APPS_DIR.path('.env'))
env = environ.Env()
if env.bool('READ_ENVFILE', default=True):
    env.read_env(ENV_PATH)


# URLs
BASE_URL = env.str("BASE_URL", default="localhost:8000")

# Login URL
LOGIN_URL='/login'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY', default='r((ws^80$x*0sm6wdvqgi&l@eea^f@%!+9%ah35gcas6oukgj#')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', True)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=['localhost'])

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'runner'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'flow.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(APPS_DIR.path('templates'))],
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

WSGI_APPLICATION = 'flow.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASE_URL = 'sqlite:///db.sqlite3'
POSTGRES_HOST = env('POSTGRES_HOST', default=None)
POSTGRES_DB = env('POSTGRES_DB', default=None)
POSTGRES_USER = env('POSTGRES_USER', default=None)
POSTGRES_PASSWORD = env('POSTGRES_PASSWORD', default=None)
if POSTGRES_DB and POSTGRES_USER and POSTGRES_PASSWORD and POSTGRES_HOST:
    DATABASE_URL = 'postgres://' + POSTGRES_USER + ':' + POSTGRES_PASSWORD + '@' + POSTGRES_HOST + '/' + POSTGRES_DB

DATABASES = {
    'default': env.db('DATABASE_URL', default=DATABASE_URL),
}
DATABASES['default']['ATOMIC_REQUESTS'] = True
DATABASES['default']['CONN_MAX_AGE'] = 600

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

# STATIC_ROOT = env.str("DJANGO_STATIC_ROOT", default=str(APPS_DIR.path('assets')))
STATIC_URL = env.str("DJANGO_STATIC_URL", default='/static/')
STATICFILES_DIRS = (os.path.join(str(APPS_DIR), "assets"), )


# Design path on the file system
STORAGE_DIR = env.str("STORAGE_DIR", default=str(APPS_DIR.path('storage')))
FLOW_TEMPLATE_DIR = env.str("FLOW_TEMPLATE_DIR", default=str(APPS_DIR.path('flow.sample')))
REPOS_TMP_DIR = env.str("REPOS_TMP_DIR", default=str(APPS_DIR.path('repos_tmp')))


# Storage Web URL
STORAGE_URL = env.str("STORAGE_URL", default='http://localhost')

# OpenROAD URL
OPENROAD_URL = env.str("OPENROAD_URL", default='http://localhost')

# Celery Stuff
BROKER_URL = env.str("BROKER_URL", default='redis://localhost:6379')
CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND", default='redis://localhost:6379')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/New_York'

# Live Monitoring Stuff
LIVE_MONITORING_URL=env.str("LIVE_MONITORING_URL", default='localhost')
LIVE_MONITORING_PASSWORD=env.str("LIVE_MONITORING_PASSWORD", default='')