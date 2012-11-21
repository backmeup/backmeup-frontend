# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'project.views.home', name='home'),
    # url(r'^project/', include('project.foo.urls')),
    
    # admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    
    # frontend
    url(r'^$', 'main.views.index', name="index"),
    
    url(r'^signup/$', 'access.views.signup', name="signup"),
    url(r'^verify_email/$', 'access.views.verify_email', name="verify-email"),
    url(r'^verify_email/(?P<verify_hash>\w+)/$', 'access.views.verify_email', name="verify-email"),
    url(r'^verify_email_resend/$', 'access.views.verify_email_resend', name="verify-email-resend"),
    url(r'^user_settings/$', 'access.views.user_settings', name="user-settings"),
    
    url(r'^accounts/login/$', 'access.views.login', {'template_name': 'www/access/login.html'}),
    url(r'^accounts/logout/$', 'access.views.logout', {'next_page': '/'}),
    
    url(r'^datasource/select/$', 'main.views.datasource_select', name="datasource-select"),
    url(r'^datasource/auth/$', 'main.views.datasource_auth', name="datasource-auth"),
    
    url(r'^datasink/select/$', 'main.views.datasink_select', name="datasink-select"),
    url(r'^datasink/auth/$', 'main.views.datasink_auth', name="datasink-auth"),
    
    url(r'^oauth_callback/$', 'main.views.oauth_callback', name="oauth-callback"),
    
    url(r'^job/create/$', 'main.views.job_create', name="job-create"),
    url(r'^job/(?P<job_id>\d+)/log$', 'main.views.job_log', name="job-log"),
    
    url(r'^search/$', 'main.views.search', name='search'),
    url(r'^search/(?P<search_id>\d+)/$', 'main.views.search_result', name='search-result'),
    url(r'^search/(?P<search_id>\d+)/(?P<file_id>[\w\d:]+)/$', 'main.views.file_info', name='file-info'),
    
    # styleguide
    (r'^styleguide$', TemplateView.as_view(template_name='www/styleguide/styleguide.html')),
    
    # dummy-templates
    (r'^search-result$', TemplateView.as_view(template_name='www/search_result.html')),
    (r'^search-result-detail$', TemplateView.as_view(template_name='www/search_result_detail.html')),
    
)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )

# static files
urlpatterns += staticfiles_urlpatterns()

### DEBUG urls
if settings.DEBUG:
    
    # media
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
