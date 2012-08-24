# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.views.generic import TemplateView

from filebrowser.sites import site

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'project.views.home', name='home'),
    # url(r'^project/', include('project.foo.urls')),
    
    # admin
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    
    # frontend
    url(r'^$', 'main.views.index', name="index"),
    
    url(r'^signup/$', 'access.views.signup', name="signup"),
    url(r'^verify_email/$', 'access.views.verify_email', name="verify-email"),
    url(r'^verify_email/(?P<verify_hash>\w+)/$', 'access.views.verify_email', name="verify-email"),
    
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'www/access/login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    
    url(r'^select_datasource/$', 'main.views.select_datasource', name="select-datasource"),
    url(r'^auth_datasource/$', 'main.views.auth_datasource', name="auth-datasource"),
    
    
    
    # styleguide
    (r'^styleguide$', TemplateView.as_view(template_name='www/styleguide/styleguide.html')),

)


### DEBUG urls
if settings.DEBUG:
    # static files
    urlpatterns += staticfiles_urlpatterns()
    
    # media
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
