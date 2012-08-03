# coding: utf-8

import sys
import os

# same as settings.BASE_ROOT and settings.PROJECT_ROOT
BASE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
PROJECT_ROOT = os.path.join(BASE_ROOT, 'project')

sys.path = [
    PROJECT_ROOT,
    os.path.join(BASE_ROOT, 'lib'),
] + sys.path

# add site packages from viratualenv.
# NOTE: maybe obsolet
import site
site.addsitedir('/data/backmeup-frontend-env/lib/python2.6/site-packages')

# restart wsgi process if source file are changed
#import monitor
#monitor.start(interval=1.0)
#monitor.track(os.path.join(os.path.dirname(__file__), 'backmeup.vhost.conf'))

# Avoid ``[Errno 13] Permission denied: '/var/www/.python-eggs'`` messages
os.environ['PYTHON_EGG_CACHE'] = '/data/backmeup-frontend-env/mod_wsgi/egg-cache'

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()


#
# to test if config works
#
#def application(environ, start_response):
#    status = '200 OK'
#    output = 'Hello World!'
#
#    response_headers = [('Content-type', 'text/plain'),
#                        ('Content-Length', str(len(output)))]
#    start_response(status, response_headers)
#
#    return [output]