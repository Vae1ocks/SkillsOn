import os
from .base import *

DEBUG = False

ADMINS = [
    ('Vaelocks', 'email@email.com'),
]

ALLOWED_HOSTS = ['auth-service','31.128.42.26']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': 'db_auth',
        'PORT': '5432',
    },
}

CELERY_BROKER_URL = 'amqp://guest:guest@rabbitmq:5672'

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'idin64394@gmail.com'
EMAIL_HOST_PASSWORD = 'byng elnn bcyb tfnh'
EMAIL_PORT = 587
EMAIL_USE_TLS = True