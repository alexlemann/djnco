from djnco.settings import *

DEBUG = True

STATICFILES_DIRS = (
    '/Users/alexlemann/projects/djnco/static/',
    ('encoder', '/Users/alexlemann/projects/djnco/encoder/static'),
)
TEMPLATE_DIRS = ('/Users/alexlemann/projects/djnco/templates', )

DATABASES = {
    'default': {
        'ENGINE': 'sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'test.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

UPLOAD_DIR='/Users/alexlemann/projects/djnco/media/incoming/'
ENCODESRC_DIR='/Users/alexlemann/projects/djnco/media/encode_src/'
ENCODEDST_DIR='/Users/alexlemann/projects/djnco/media/encode_dst/'
PUBLISH_DIR='/Users/alexlemann/projects/djnco/media/published/'

import djcelery
djcelery.setup_loader()
BROKER_HOST = 'localhost'
BROKER_PORT = 5672
BROKER_VHOST = 'djnco'
BROKER_USER = 'djnco'
BROKER_PASSWORD = 'password'

CELERY_CONCURRENCY = 1

SECRET_KEY = 'cvgw6=$q0(!w&5*nt324qy^jmn#ahdufzx!_8-_1-gaf8woqmn'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
