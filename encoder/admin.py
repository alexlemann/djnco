from django.contrib import admin
from djnco.encoder import models as encoder


class CollectionAdmin(admin.ModelAdmin):
    readonly_fields = ('to_be_encoded', 'encode_button', 'to_be_imported',
        'import_button', )
    fieldsets = (
        (None, {
           'fields': ('slug', ),
        }), )
    change_fieldsets = (
        ('Encoding Actions', {
            'fields': ('to_be_encoded', 'encode_button', ),
        }),
        ('Import Actions', {
            'fields': ('to_be_imported', 'import_button', ),
        }), )

    #Show special links to import media when editing a collection, not when
    #   adding one.
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.fieldsets
        else:
            return self.fieldsets + self.change_fieldsets
admin.site.register(encoder.Collection, CollectionAdmin)


class MediaAdmin(admin.ModelAdmin):
    readonly_fields = ('get_identifier', 'original_filename',
        'encoding_started', 'encoding_finished', 'queued_time',
        'encode_start_time', 'encode_end_time', )
    list_display = ('original_filename', 'title', 'collection',
        'get_identifier', 'encoding_started', 'encoding_finished',
        'view_on_site', )
    list_filter = ('collection', )
    fieldsets = (
        (None, {
            'fields':
              ('original_filename', 'collection', 'get_identifier',
               'date', 'title', 'description', ),
        }),
        ('Timing', {
            'fields':
              ('queued_time', 'encode_start_time', 'encode_end_time', ),
        }), )
admin.site.register(encoder.Video, MediaAdmin)
admin.site.register(encoder.Audio, MediaAdmin)
