=====
djnco
=====

What is Djnco
=============

Djnco is a media encoding and publishing server built using Django.

Getting Started
===============

Download and install djnco and requirements::

   $ git clone git://github.com/lemanal/djnco.git
   $ cd djnco
   $ pip install -r requirements.txt

Edit the local settings (see below)::

   # Start up djnco & celery in separate shells
   $ python ./manage.py runserver
   $ python ./manage.py celeryd -E
   $ python ./manage.py celerycam
 
Djnco Settings
==============
 
A directory where media collections will be uploaded.
   UPLOAD_DIR = '/home/ablemann/projects/djnco/djnco/incoming/'
A working directory where encoded media will be copied to before encoding begins
   ENCODESRC_DIR='/home/ablemann/projects/djnco/djnco/encode_source/'
A working directory where encoded media will end up as it is encoded
   ENCODEDST_DIR='/mnt/encode_dst/'
Once an encoding process completes it will copy encoded files here as a publish point
   PUBLISH_DIR='/mnt/published/'
These are the formats that are accepted as input for media
   INCOMING_FORMATS = { 
    'video' : ('mp4','mov','avi','m4v','wmv','mpg','ogv', 'mkv', 'ts'),
    'audio' : ('wave', 'wav', 'mp3', 'wma', 'aac', 'flac', 'm1a')
   }
Video is automatically encoded in multiple bitrates so that scaling can be done based on the amount of available bandwidth
   VIDEO_BITRATES=['600','1024']

Additionally, a number of django-celery settings are required. For more information see: https://github.com/ask/django-celery
Furthermore, normal Django settings are required, specifically a database must be defined.
