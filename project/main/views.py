# -*- coding: utf-8 -*-


from django.contrib.auth.decorators import login_required
#from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

from remote_api.rest import RestDatasource

from main.forms import DatasourceSelectForm, DatasourceAuthForm, DatasinkSelectForm

def index(request):
    context = {}
    return render_to_response(
        "www/index.html",
        context,
        context_instance=RequestContext(request)
    )


@login_required
def select_datasource(request):
    form = DatasourceSelectForm(request.POST or None)
    if form.is_valid():
        #request.session['key_ring'] = form.cleaned_data['key_ring']
        auth_data = form.rest_save(username=request.user.username)
        print "@@@@@@@@@@@@@@@@@@@@@@@@auth_data", auth_data
        if auth_data:
            request.session['auth_data'] = auth_data
            print "####################################JOJO select_datasource"
            return redirect('auth-datasource')
    print "@@@@@@@@@@@@@@@@@@@@@@@@@@WTF!!!"
    return render_to_response(
        "www/select_datasource.html",
        {
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@login_required
def auth_datasource(request):
    
    print "####################################JOJO auth_datasource"
    #if not 'auth_data' in request.session:
    #    print "#############################################################NOOOOOOOOOO"
    #    messages.add_message(request, messages.ERROR, 'Some error occured. It seems like you didn\'t select any datasource. please do here.')
    #    redirect('select-datasource')
    
    form = DatasourceAuthForm(request.POST or None, auth_data=request.session['auth_data'])
    
    if form.is_valid():
        result = form.rest_save(username=request.user.username, auth_data=request.session['auth_data'])
        request.session['datasource_profile_id'] = request.session['auth_data']['profileId']
        del request.session['auth_data']
        return redirect('select-datasink')
    
    return render_to_response(
        "www/auth_datasource.html",
        {
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@login_required
def select_datasink(request):
    form = DatasinkSelectForm(request.POST or None)
    if form.is_valid():
        #request.session['key_ring'] = form.cleaned_data['key_ring']
        auth_data = form.rest_save(username=request.user.username)
        print "@@@@@@@@@@@@@@@@@@@@@@@@auth_data", auth_data
        if auth_data:
            request.session['auth_data'] = auth_data
            print "####################################JOJO select_datasource"
            return redirect('auth-datasource')
    print "@@@@@@@@@@@@@@@@@@@@@@@@@@WTF!!!"
    return render_to_response(
        "www/select_datasink.html",
        {
            'form': form,
        },
        context_instance=RequestContext(request)
    )
