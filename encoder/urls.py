from django.conf.urls.defaults import patterns, include, url

from djnco.encoder import views as enc_views

urlpatterns = patterns('',
    url(r'encode_collection/(?P<collection_slug>\w+)',
        enc_views.encode_collection,
        name='encode_collection'),
    url(r'import_collection/(?P<collection_slug>\w+)',
        enc_views.import_collection,
        name='import_collection'),
    url(r'^$',
        enc_views.home,
        name='home'),
    url(r'play/(?P<identifier>[\w\d\-]+)',
        enc_views.media_player,
        name='media_player'),
    url(r'comment/delete/(?P<comment_id>\d+)$',
        enc_views.delete_comment,
        name='delete_comment'),
    url(r'comment/delete/(?P<comment_id>\d+)/confirm$',
        enc_views.delete_comment_confirm,
        name='delete_comment_confirm'),
)
