import os
from .base import *

DEBUG = True

# ADMINS = [
#     ('Vaelocks', 'email@email.com'),
# ]

# ALLOWED_HOSTS = ['courses-service', '31.128.42.26']
ALLOWED_HOSTS = ['*']

REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = (
    'rest_framework_simplejwt.authentication.JWTStatelessUserAuthentication',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': 'db_courses',
        'PORT': '5432',
    },
}

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'idin64394@gmail.com'
EMAIL_HOST_PASSWORD = 'byng elnn bcyb tfnh'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

CELERY_BROKER_URL = 'amqp://guest:guest@rabbitmq:5672'