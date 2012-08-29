# -*- coding: utf-8 -*-


from django.contrib.auth.decorators import login_required
#from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

#from remote_api.rest import RestDatasinkProfile

from main.forms import DatasourceSelectForm, DatasourceAuthForm, DatasinkSelectForm, DatasinkAuthForm

def index(request):
    context = {}
    return render_to_response(
        "www/index.html",
        context,
        context_instance=RequestContext(request)
    )


@login_required
def select_datasource(request):
    print "####################################view: select_datasource"
    form = DatasourceSelectForm(request.POST or None)
    if form.is_valid():
        #request.session['key_ring'] = form.cleaned_data['key_ring']
        auth_data = form.rest_save(username=request.user.username)
        if auth_data:
            request.session['auth_data'] = auth_data
            if auth_data['type'] == 'OAuth':
                request.session['next_step'] = 'auth-datasource'
                return redirect(auth_data['redirectURL'])
            return redirect('auth-datasource')
    return render_to_response(
        "www/select_datasource.html",
        {
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@login_required
def auth_datasource(request):
    print "####################################view: auth_datasource"
    #if not 'auth_data' in request.session:
    #    print "#############################################################NOOOOOOOOOO"
    #    messages.add_message(request, messages.ERROR, 'Some error occured. It seems like you didn\'t select any datasource. please do here.')
    #    redirect('select-datasource')
    
    form = DatasourceAuthForm(request.POST or None, auth_data=request.session['auth_data'])
    
    if form.is_valid():
        result = form.rest_save(username=request.user.username)
        if not result == False:
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
    print "####################################view: select_datasink"
    form = DatasinkSelectForm(request.POST or None)
    if form.is_valid():
        #request.session['key_ring'] = form.cleaned_data['key_ring']
        auth_data = form.rest_save(username=request.user.username)
        if auth_data:
            request.session['auth_data'] = auth_data
            if auth_data['type'] == 'OAuth':
                request.session['next_step'] = 'auth-datasink'
                return redirect(auth_data['redirectURL'])
            return redirect('auth-datasink')
    return render_to_response(
        "www/select_datasink.html",
        {
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@login_required
def auth_datasink(request):
    print "####################################view: auth_datasink"
    #if not 'auth_data' in request.session:
    #    print "#############################################################NOOOOOOOOOO"
    #    messages.add_message(request, messages.ERROR, 'Some error occured. It seems like you didn\'t select any datasink. please do here.')
    #    redirect('select-datasink')
    
    form = DatasinkAuthForm(request.POST or None, auth_data=request.session['auth_data'])

    if form.is_valid():
        result = form.rest_save(username=request.user.username)
        request.session['datasink_profile_id'] = request.session['auth_data']['profileId']
        del request.session['auth_data']
        return redirect('select-datasink')

    return render_to_response(
        "www/auth_datasink.html",
        {
            'form': form,
        },
        context_instance=RequestContext(request)
    )

@login_required
def oauth_callback(request):
    
    request.session['auth_data']['oauth_data'] = request.GET.copy()
    
    next = request.session['next_step']
    
    valid_redirects = [
        'auth-datasink',
        'auth-datasource',
    ]
    
    if next in valid_redirects:
        del request.session['next_step']
        return redirect(next)
