# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
#from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _


from remote_api.rest import RestJobs
from main.forms import DatasourceSelectForm, DatasourceAuthForm, DatasinkSelectForm, DatasinkAuthForm, CreateJobForm, DatasourceOptionsForm


def index(request):
    context = {}
    if request.user.is_authenticated():
        rest_jobs = RestJobs(username=request.user.username)
        result = rest_jobs.get_all()

        if result and 'errorType' in result:
            messages.error(request, _(result['errorType']))
        else:
            context['jobs'] = result

    return render_to_response(
        "www/index.html",
        context,
        context_instance=RequestContext(request))


@login_required
def datasource_select(request):
    form = DatasourceSelectForm(request.POST or None)
    if form.is_valid():
        #request.session['key_ring'] = form.cleaned_data['key_ring']
        auth_data = form.rest_save(username=request.user.username, key_ring=request.session['key_ring'])
        if auth_data:
            request.session['auth_data'] = auth_data
            if auth_data['type'] == 'OAuth':
                request.session['next_step'] = 'datasource-auth'
                return redirect(auth_data['redirectURL'])
            return redirect('datasource-auth')
    return render_to_response(
        "www/datasource_select.html",
        {
            'form': form,
        },
        context_instance=RequestContext(request))


@login_required
def datasource_auth(request):
    #if not 'auth_data' in request.session:
    #    print "#############################################################NOOOOOOOOOO"
    #    messages.add_message(request, messages.ERROR, 'Some error occured. It seems like you didn\'t select any datasource. please do here.')
    #    redirect('datasource-select')

    form = DatasourceAuthForm(request.POST or None, username=request.user.username, auth_data=request.session['auth_data'])

    if form.is_valid():
        result = form.rest_save(username=request.user.username, key_ring=request.session['key_ring'])
        if not result == False:
            request.session['datasource_profile_id'] = request.session['auth_data']['profileId']
            return redirect('datasource-options')

    return render_to_response(
        "www/datasource_auth.html",
        {
            'form': form,
        },
        context_instance=RequestContext(request))


@login_required
def datasource_options(request):
    
    form = DatasourceOptionsForm(request.POST or None, username=request.user.username, auth_data=request.session['auth_data'], key_ring=request.session['key_ring'])

    if form.is_valid():
        del request.session['auth_data']
        form.rest_save()
        
    return render_to_response(
        "www/datasource_options.html",
        {
            'form': form,
        },
        context_instance=RequestContext(request))


@login_required
def datasink_select(request):
    form = DatasinkSelectForm(request.POST or None)
    if form.is_valid():
        #request.session['key_ring'] = form.cleaned_data['key_ring']
        auth_data = form.rest_save(username=request.user.username, key_ring=request.session['key_ring'])
        if auth_data:
            request.session['auth_data'] = auth_data
            if auth_data['type'] == 'OAuth':
                request.session['next_step'] = 'datasink-auth'
                return redirect(auth_data['redirectURL'])
            return redirect('datasink-auth')
    return render_to_response(
        "www/datasink_select.html",
        {
            'form': form,
        },
        context_instance=RequestContext(request))


@login_required
def datasink_auth(request):
    #if not 'auth_data' in request.session:
    #    print "#############################################################NOOOOOOOOOO"
    #    messages.add_message(request, messages.ERROR, 'Some error occured. It seems like you didn\'t select any datasink. please do here.')
    #    redirect('datasink-select')

    form = DatasinkAuthForm(request.POST or None, auth_data=request.session['auth_data'])

    if form.is_valid():
        result = form.rest_save(username=request.user.username)
        request.session['datasink_profile_id'] = request.session['auth_data']['profileId']
        del request.session['auth_data']
        return redirect('create-job')

    return render_to_response(
        "www/datasink_auth.html",
        {
            'form': form,
        },
        context_instance=RequestContext(request))


@login_required
def datasink_options(request):
    pass


@login_required
def oauth_callback(request):
    request.session['auth_data']['oauth_data'] = request.GET.copy()
    
    next = request.session['next_step']

    valid_redirects = [
        'datasink-auth',
        'datasource-auth',
    ]

    if next in valid_redirects:
        del request.session['next_step']
        return redirect(next)


@login_required
def create_job(request):
    form = CreateJobForm(request.POST or None, username=request.user.username)

    if form.is_valid():
        result = form.rest_save()
        if result:
            return redirect('index')

    return render_to_response(
        "www/create_job.html",
        {
            'form': form,
        },
        context_instance=RequestContext(request))
