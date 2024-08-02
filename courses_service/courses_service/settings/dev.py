from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = (
    'rest_framework_simplejwt.authentication.JWTAuthentication',
    'rest_framework.authentication.SessionAuthentication',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'courses_service',
        'USER': 'admin',
        'PASSWORD': 'admin',
    },
}

CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672'