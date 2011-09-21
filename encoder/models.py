from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django_extensions.db.fields import UUIDField

from encoder.encode_tasks import encode_video, encode_audio

import os
import datetime
import shutil

class Collection(models.Model):
    slug = models.SlugField(max_length=20, unique=True)

    def encode(self):
        for v in Video.objects.filter(collection=self, encoding_started=False, encoding_finished=False):
            v.encode()
        for a in Audio.objects.filter(collection=self, encoding_started=False, encoding_finished=False):
            a.encode()

    def import_media(self):
        files = os.listdir(settings.UPLOAD_DIR + self.slug + '/')
        for f in files:
            for media_type, extensions in settings.INCOMING_FORMATS.items():
                if any([f.endswith(ext) for ext in extensions]):
                    orig_path = os.path.join(settings.UPLOAD_DIR, self.slug, f)
                    if media_type == 'video':
                        media = Video(collection=self, upload=orig_path)
                    elif media_type == 'audio':
                        media = Audio(collection=self, upload=orig_path)
                    media.save()
                    shutil.move(orig_path, media.encode_src())
                    from django.core.files.base import File
                    media.upload.file = File(media.encode_src())
                    media.save()

    def to_be_imported(self):
        try:
            files = os.listdir(settings.UPLOAD_DIR + self.slug + '/')
        except OSError:
            return 'Directory: ' + self.slug + ' not found'
        for f in files:
            found = False
            for media_type, extensions in settings.INCOMING_FORMATS.items():
                if any([f.endswith(ext) for ext in extensions]):
                    found = True
            if not found:
                files.remove(f)
        if files:
            return '<br />'.join(files)
        else:
            return 'No files available for importing'
    to_be_imported.short_description = 'To Be Imported'
    to_be_imported.allow_tags = True

    def import_button(self):
        return '<a href="/encoder/import_collection/' + self.slug + '">Import</a>'
    import_button.short_description = 'Uploaded Files'
    import_button.allow_tags = True

    def to_be_encoded(self):
        media = self.media.filter(encoding_started=False)
        if media:
            return '<br />'.join([m.original_filename for m in media])
        else:
            return 'No videos available for encoding'
    to_be_encoded.short_description = 'Import Files'
    to_be_encoded.allow_tags = True

    def encode_button(self):
        return '<a href="/encoder/encode_collection/' + self.slug + '">Start Encoding</a>'
    encode_button.short_description = 'Encode Them'
    encode_button.allow_tags = True

    def __unicode__(self):
        return self.slug

class Media(models.Model):
    def encode_src(self, *args):
        return os.path.join(settings.ENCODESRC_DIR, self.identifier)

    collection = models.ForeignKey('Collection', related_name='media')
    identifier = UUIDField(unique=True)
    original_filename = models.CharField(max_length=1024)
    upload = models.FileField(upload_to=encode_src)

    #metadata fields
    description = models.TextField(null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    #encoding stats
    encoding_started = models.BooleanField(default=False)
    encoding_finished = models.BooleanField(default=False)
    queued_time = models.DateTimeField(null=True, default=None)
    encode_start_time = models.DateTimeField(null=True, default=None)
    encode_end_time = models.DateTimeField(null=True, default=None)

    def __unicode__(self):
        return "Media, %s, %s" % (self.collection.slug, self.identifier)

    def get_identifier(self):
        if self.encoding_started and self.encoding_finished:
            return self.identifier
        else:
            return ''
    get_identifier.short_description = 'Identifier'

    def view_on_site(self):
        return ''

    def save(self, *args, **kwargs):
        self.original_filename = os.path.basename(self.upload.name)
        self.upload.filename = self.identifier
        return super(Media, self).save(*args, **kwargs)

class Audio(Media):
    def encode(self):
        self.queued_time = datetime.datetime.now()
        self.encoding_started = True
        self.save()
        encode_audio.delay(self)

    def encode_dst(self, bitrate):
        return os.path.join(settings.ENCODEDST_DIR, self.identifier) + '-' + str(bitrate) + '.mp3'

    def publish_path(self, bitrate):
        return os.path.join(settings.PUBLISH_DIR, self.identifier) + '-' + str(bitrate) + '.mp3'

    def view_on_site(self):
        if self.encoding_finished:
            return '<a href="' + reverse('demo_audio', kwargs={'identifier':self.identifier}) + '">Preview</a>'
        else:
            return 'Preview'
    view_on_site.allow_tags = True

class Video(Media):
    def encode(self):
        self.queued_time = datetime.datetime.now()
        self.encoding_started = True
        self.save()
        encode_video.delay(self)

    def encode_dst(self, bitrate):
        return os.path.join(settings.ENCODEDST_DIR, self.identifier) + '-' + bitrate + '.mp4'

    def publish_path(self, bitrate):
        return os.path.join(settings.PUBLISH_DIR, self.identifier) + '-' + bitrate + '.mp4'

    def view_on_site(self):
        if self.encoding_finished:
            return '<a href="' + reverse('demo_video', kwargs={'identifier':self.identifier}) + '">Preview</a>'
        else:
            return 'Preview'
    view_on_site.allow_tags = True
