import os

SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    'django-insecure-local-change-this-before-production',
)

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
