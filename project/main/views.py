# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from remote_api.rest import RestDatasource

def index(request):
    context = {}
    return render_to_response(
        "www/index.html",
        context,
        context_instance=RequestContext(request)
    )


def create_backup(request):
    rest_datasource = RestDatasource()
    datasources = rest_datasource.get_all()
    
    context = {
        'datasources': datasources,
    }
    return render_to_response(
        "www/create_backup.html",
        context,
        context_instance=RequestContext(request)
    )