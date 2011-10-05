from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^encoder/', include('djnco.encoder.urls')),

    url(r'^accounts/login$', 'django.contrib.auth.views.login',
        name='auth_login'),
    url(r'^accounts/logout$', 'django.contrib.auth.views.logout',
        name='auth_logout'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
