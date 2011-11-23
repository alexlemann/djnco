import os
import datetime
import shutil

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django_extensions.db.fields import UUIDField
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import File

from encoder.encode_tasks import encode_video, encode_audio


class Collection(models.Model):
    slug = models.SlugField(max_length=20, unique=True)

    def encode(self):
        query = models.Q(collection=self, encoding_started=False)
        media = list(Video.objects.filter(query))
        media += list(Audio.objects.filter(query))
        for m in media:
            m.encode()

    def import_media(self):
        collection_path = os.path.join(settings.UPLOAD_DIR, self.slug)
        media = self.to_be_imported()
        for f in media['videos']:
            orig_path = os.path.join(collection_path, f)
            media = Video(collection=self, upload=orig_path)
            media.save()
            shutil.move(orig_path, media.encode_src())
            media.upload.file = File(media.encode_src())
            media.save()
        for f in media['audio']:
            orig_path = os.path.join(collection_path, f)
            media = Audio(collection=self, upload=orig_path)
            media.save()
            shutil.move(orig_path, media.encode_src())
            media.upload.file = File(media.encode_src())
            media.save()

    def to_be_imported(self):
        from collections import defaultdict
        media = defaultdict(list)
        collection_path = os.path.join(settings.UPLOAD_DIR, self.slug)
        files = os.listdir(collection_path)
        for f in files:
            for media_type, extensions in settings.INCOMING_FORMATS.items():
                if any([f.endswith(ext) for ext in extensions]):
                    media[media_type].append(f)
        return media

    def to_be_imported_html(self):
        try:
            media = self.to_be_imported()
        except OSError:
            return 'Directory: ' + self.slug + ' not found'
        files = []
        for type, f in media.items():
            files += f
        if files:
            return '<br />'.join(files)
        else:
            return 'No files available for importing'
    to_be_imported.short_description = 'To Be Imported'
    to_be_imported.allow_tags = True

    def import_button(self):
        import_url = reverse('import_collection',
                             kwargs={'collection_slug': self.slug})
        return '<a href="%s">Import</a>' % (import_url)
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
        encode_url = reverse('encode_collection',
                             kwargs={'collection_slug': self.slug})
        return '<a href="%s">Encode</a>' % (encode_url)
    encode_button.short_description = 'Encode Them'
    encode_button.allow_tags = True

    def get_absolute_url(self):
        return reverse('collection', args=[self.slug])

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

    def get_absolute_url(self):
        return reverse('media_player', args=[self.identifier])

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
        path = os.path.join(settings.ENCODEDST_DIR, self.identifier)
        path += '-' + bitrate + '.mp3'
        return path

    def publish_path(self, bitrate):
        path = os.path.join(settings.PUBLISH_DIR, self.identifier)
        path += '-' + bitrate + '.mp3'
        return path

    def view_on_site(self):
        if self.encoding_finished:
            player_url = reverse('media_player',
                                 kwargs={'identifier': self.identifier})
            return '<a href="%s">Preview</a>' % (player_url)
        else:
            return 'Preview'
    view_on_site.allow_tags = True

    def get_absolute_url(self):
        return reverse('media_player', args=[self.identifier])


class Video(Media):
    def encode(self):
        self.queued_time = datetime.datetime.now()
        self.encoding_started = True
        self.save()
        encode_video.delay(self)

    def encode_dst(self, bitrate):
        path = os.path.join(settings.ENCODEDST_DIR, self.identifier)
        path += '-' + bitrate + '.mp4'
        return path

    def publish_path(self, bitrate):
        path = os.path.join(settings.PUBLISH_DIR, self.identifier)
        path += '-' + bitrate + '.mp4'
        return path

    def view_on_site(self):
        if self.encoding_finished:
            player_url = reverse('media_player',
                                 kwargs={'identifier': self.identifier})
            return '<a href="%s">Preview</a>' % (player_url)
        else:
            return 'Preview'
    view_on_site.allow_tags = True

    def get_absolute_url(self):
        return reverse('media_player', args=[self.identifier])


class Comment(models.Model):
    commenter = models.ForeignKey(User, related_name='comments')
    media = models.ForeignKey('Media', related_name='commments')
    created_time = models.DateTimeField(null=False, default=None)
    last_modified_time = models.DateTimeField(null=False, default=None)
    text = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.created_time:
            self.created_time = datetime.datetime.now()
        self.last_modified_time = datetime.datetime.now()
        return super(Comment, self).save(*args, **kwargs)


class CommentNotification(models.Model):
    comment = models.ForeignKey('Comment', related_name='notifications')
    created_time = models.DateTimeField()
    seen_time = models.DateTimeField(null=True, default=None)
    sender = models.ForeignKey(User, related_name='sent_notifications')
    receiver = models.ForeignKey(User, related_name='received_notifications')

    class Meta:
        unique_together = (("comment", "receiver"),)

    def seen():
        return bool(seen_time)
