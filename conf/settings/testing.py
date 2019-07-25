from .base import *
import logging

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'PORT': 5432,
        'NAME': 'test_db',
        'USER': 'development',
        'PASSWORD': 'development',
    }
}

# we don't want logging while running tests.
logging.disable(logging.CRITICAL)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

DEBUG = False
TEMPLATE_DEBUG = DEBUG
TESTS_IN_PROGRESS = True

MEDIA_ROOT = 'tests_media/'

