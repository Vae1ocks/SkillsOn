from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'auth_service',
        'USER': 'admin',
        'PASSWORD': 'admin',
    },
}

CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'