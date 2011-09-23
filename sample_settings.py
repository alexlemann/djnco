from djnco.settings import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'djnco_production',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

UPLOAD_DIR='/home/ablemann/projects/djnco/djnco/incoming/'
ENCODESRC_DIR='/home/ablemann/projects/djnco/djnco/encode_source/'
ENCODEDST_DIR='/mnt/encode_dst/'
PUBLISH_DIR='/mnt/published/'

import djcelery
djcelery.setup_loader()
BROKER_HOST = 'localhost'
BROKER_PORT = 5672
BROKER_VHOST = 'djnco'
BROKER_USER = 'djnco'
BROKER_PASSWORD = 'password'

CELERY_CONCURRENCY = 1
