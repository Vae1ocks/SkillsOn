import os
from .base import *

DEBUG = False

ADMINS = [
    ('Vaelocks', 'email@email.com'),
]

ALLOWED_HOSTS = ['user-service', '31.128.42.26']

REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = (
    'rest_framework_simplejwt.authentication.JWTAuthentication',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'user_service',
        'USER': 'admin',
        'PASSWORD': 'admin',
        'HOST': 'db_user',
        'PORT': '5432',
    }
}

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

CELERY_BROKER_URL = 'amqp://guest:guest@rabbitmq:5672'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis', 6379)],
        }
    }
}

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'idin64394@gmail.com'
EMAIL_HOST_PASSWORD = 'byng elnn bcyb tfnh'
EMAIL_PORT = 587
EMAIL_USE_TLS = True