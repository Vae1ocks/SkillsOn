"""
Django settings for courses_service project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-+w_!57f!=n0_wlm01bnr_1ptqs%k#apvjs#nxh=lymua$($gc1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['courses-service', 'localhost', '127.0.0.1', '31.128.42.26']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    "corsheaders",
    'courses.apps.CoursesConfig',
    'payment.apps.PaymentConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}


ROOT_URLCONF = 'courses_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'courses_service.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'courses_service',
        'USER': 'admin',
        'PASSWORD': 'admin',
        'HOST': 'db_courses',
        'PORT': 5432,
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CORS_ALLOW_ALL_ORIGINS: True

CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)

CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
)

from kombu import Queue, Exchange

CELERY_BROKER_URL = 'amqp://guest:guest@rabbitmq:5672'
CELERY_result_backend = 'rpc://'
CELERY_accept_content = ['json']
CELERY_task_serializer = 'json'
CELERY_result_serializer = 'json'
CELERY_timezone = 'UTC'
CELERY_imports = (
    'courses.tasks',
)
'''
CELERY_QUEUES = (
    Queue('courses_service_queue', Exchange('courses_service', type='topic'),
          routing_key='courses_service.#')
)
CELERY_ROUTES = {
    'courses_service.*': {
        'queue': 'courses_service_queue',
        'routing_key': 'courses_service.#'
    }
}
'''
YOOKASSA_SECRET_KEY = 'test_XNy-Fi909xFYLCXW6w-mMZBIfIjEm4vHgQA3H4WhDZs'
YOOKASSA_ACCOUNT_ID = 415869

STRIPE_PUBLISHABLE_KEY = 'pk_test_51PaL6LHb3jL9c0IRhxuw3RsyJ92XZ8uEDFyoFx27ZI0Lj3CunpbOH7myayJHuYa0DfklCY3HBXlyWOo3m1IiSX2Q008pYIirPP'
STRIPE_SECRET_KEY = 'sk_test_51PaL6LHb3jL9c0IRXodzo4fbrf2EcbjE5mh9GRAFtYYLrtCVd0TyegEbZsnjfys2eORwAqLqPCcFn4pbR1gMTwLk00Kc7jKG50'
STRIPE_API_VERSION = '2024-06-20'
STRIPE_WEBHOOK_SECRET = 'whsec_cc8fc5687aa0de6e0a1aca8f971048160e032d076dc003a9f849bd0e1d3c08e5'

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False