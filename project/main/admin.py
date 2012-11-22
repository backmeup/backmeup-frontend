# -*- coding: utf-8 -*-
# no grappelli => no need for this
from django.contrib import admin

from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin


class FlatPageAdmin(FlatPageAdmin):
    class Media:
        js = [
            '/static/tinymce/jscripts/tiny_mce/tiny_mce.js',
            '/static/tinymce_setup/tinymce_setup.js',
        ]

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)

