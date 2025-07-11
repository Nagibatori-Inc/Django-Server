"""
Django settings for DjangoServer project.

Generated by 'django-admin startproject' using Django 5.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path

import structlog
from decouple import AutoConfig


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Loading `.env` files
# See docs: https://github.com/HBNetwork/python-decouple
config = AutoConfig(search_path=BASE_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-jlfaz)s(!fgo^x!y=^kxyr1huxxr^qutvna2ek3#azy_+1t__z"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default='dev') == 'debug' or 'dev' or 'development'

ALLOWED_HOSTS = ['localhost', '0.0.0.0', '127.0.0.1', '*', '[::1]']
ALLOWED_HOSTS += config('ALLOWED_HOSTS', default='').split(',')


# Application definition

INSTALLED_APPS = [
    "django_prometheus",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "knox",
    'booking.apps.BookingConfig',
    'authentication.apps.AuthenticationConfig',
    'payments.apps.PaymentsConfig',
    'support.apps.SupportConfig',
    "django_migration_linter",
    'drf_spectacular',
    'corsheaders',  # убрать когда появится nginx или caddy
    'review',
    'notification',
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = "DjangoServer.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework.authentication.BasicAuthentication',),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

WSGI_APPLICATION = "DjangoServer.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB', default='booking_platform'),
        'USER': config('POSTGRES_USER', default='admin'),
        'PASSWORD': config('POSTGRES_PASSWORD', default='adminpassword'),
        'HOST': config('DATABASE_HOST', default='localhost'),
        'PORT': config('DJANGO_DATABASE_PORT', cast=int, default=5432),
        'CONN_MAX_AGE': config('CONN_MAX_AGE', cast=int, default=60),
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=15000ms',
        },
    }
}

# Logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "loki": {
            "class": "logging_loki.LokiHandler",
            "formatter": "json",
            "url": "http://lgtm:3100/loki/api/v1/push",
            "tags": {"app": "django_app"},
            "version": "1",
        },
    },
    "formatters": {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
            "foreign_pre_chain": [
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.stdlib.add_log_level,
            ],
        },
    },
    "loggers": {
        "django": {
            "handlers": ["loki"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

HOST = config('HOST', default='http://localhost:8000/')

REST_API_BASE = config('REST_API_BASE', default='api/')


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Настройки сервиса рассылки СМС
# Используется SMSAero https://smsaero.ru/

SMSAERO_EMAIL = config("SMSAERO_EMAIL", default="johndoe@email.com")
SMSAERO_API_KEY = config("SMSAERO_API_KEY", default=None)

SMS_MODE = config("SMS_MODE", default="production")

# Шаблон отправляемого сообщения верификации (где {0} - это одноразовый код)
MESSAGE_TEMPLATE = "Ваш код, {0}"

# Время действия одноразового кода (OTP) в минутах
OTP_TTL = config("OTP_TTL", default=15)

# Настройки Celery
REDIS_HOST = config("REDIS_HOST", default="localhost")
REDIS_PORT = config("REDIS_PORT", cast=int, default=6379)

CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

# Email
EMAIL_BACKEND = config("EMAIL_BACKEND", "")
EMAIL_HOST = config("EMAIL_HOST", "")
EMAIL_PORT = config("EMAIL_PORT", "")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", False)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", True)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", "")

# Переменные ЮКассы
YOO_KASSA_SECRET = config("YOO_KASSA_SECRET", "test_LJLS5QClPXp9H6PqPXjPDAD9n6HihzEGy45951HxMII")
YOO_KASSA_ID = config("YOO_KASSA_ID", "1093728")

YOO_KASSA_IPS = (
    "185.71.76.0/27",
    "185.71.77.0/27",
    "77.75.153.0/25",
    "77.75.156.11",
    "77.75.156.35",
    "77.75.154.128/25",
    "2a02:5180::/32",
)
