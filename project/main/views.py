# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
#from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _


from remote_api.rest import RestJobs, RestDatasourceProfile, RestDatasinkProfile
from main.forms import DatasourceSelectForm, DatasourceAuthForm, DatasinkSelectForm, DatasinkAuthForm, JobCreateForm, JobDeleteForm


def get_sink_title(sinks, sink_id):
    sink_id = int(sink_id)
    for sink in sinks:
        if sink['datasinkProfileId'] == sink_id:
            return sink['title']


def get_source_title(sources, source_id):
    source_id = int(source_id)
    for source in sources:
        if source['datasourceProfileId'] == source_id:
            return source['title']
    return None


def get_job(jobs, job_id):
    job_id = int(job_id)
    for job in jobs:
        if int(job['backupJobId']) == job_id:
            return job


def additional_context(request):
    context = {}
    
    if 'datasource_profile_id' in request.session:
        rest_datasource = RestDatasourceProfile(username=request.user.username)
        context['datasource_profile'] = rest_datasource.get(request.session['datasource_profile_id'])
    
    if 'datasink_profile_id' in request.session:
        rest_datasink = RestDataskinProfile(username=request.user.username)
        context['datasource_profile'] = rest_datasink.get(request.session['datasink_profile_id'])
    
    return context


def index(request):
    context = {}
    if request.user.is_authenticated():
        
        ### delete job form start
        job_delete_form = JobDeleteForm(request.POST or None)
        if job_delete_form.is_valid():
            result = job_delete_form.rest_save(username=request.user.username)
            if result:
                messages.add_message(request, messages.SUCCESS, _(u'Backup wurde gelöscht.'))
            else:
                messages.add_message(request, messages.ERROR, _(u'Backup konnte nicht gelöscht werden.'))
        context['job_delete_form'] = job_delete_form
        
        rest_jobs = RestJobs(username=request.user.username)
        jobs = rest_jobs.get_all()
        #### delete job form end

        if jobs and 'errorType' in jobs:
            messages.error(request, _(jobs['errorType']))
        else:
            rest_datasource_profile = RestDatasourceProfile(username=request.user.username)
            datasource_profiles = rest_datasource_profile.get_all()
            
            rest_datasink_profile = RestDatasinkProfile(username=request.user.username)
            datasink_profiles = rest_datasink_profile.get_all()
            
            for job in jobs:
                job['datasinkTitle'] = get_sink_title(datasink_profiles, job['datasinkId'])
                job['datasources'] = []
                for source_id in job['datasourceIds']:
                    job['datasources'].append({
                        'id': source_id,
                        'title': get_source_title(datasource_profiles, source_id)
                    })
            context['jobs'] = jobs
            

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
        additional_context(request).update({
            'form': form,
        }),
        context_instance=RequestContext(request))


@login_required
def datasource_auth(request):
    #if not 'auth_data' in request.session:
    #    print "#############################################################NOOOOOOOOOO"
    #    messages.add_message(request, messages.ERROR, 'Some error occured. It seems like you didn\'t select any datasource. please do here.')
    #    redirect('datasource-select')

    form = DatasourceAuthForm(request.POST or None, username=request.user.username, auth_data=request.session['auth_data'])

    if form.is_valid() or request.session['auth_data']['type'] != 'Input':
        result = form.rest_save(username=request.user.username, key_ring=request.session['key_ring'])
        if not result == False:
            request.session['datasource_profile_id'] = request.session['auth_data']['profileId']
            del request.session['auth_data']
            return redirect('datasink-select')
    
    return render_to_response(
        "www/datasource_auth.html",
        additional_context(request).update({
            'form': form,
        }),
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
        additional_context(request).update({
            'form': form,
        }),
        context_instance=RequestContext(request))


@login_required
def datasink_auth(request):
    #if not 'auth_data' in request.session:
    #    print "#############################################################NOOOOOOOOOO"
    #    messages.add_message(request, messages.ERROR, 'Some error occured. It seems like you didn\'t select any datasink. please do here.')
    #    redirect('datasink-select')

    form = DatasinkAuthForm(request.POST or None, auth_data=request.session['auth_data'])
    
    if form.is_valid() or request.session['auth_data']['type'] != 'Input':
        result = form.rest_save(username=request.user.username, key_ring=request.session['key_ring'])
        request.session['datasink_profile_id'] = request.session['auth_data']['profileId']
        del request.session['auth_data']
        return redirect('job-create')
    
    return render_to_response(
        "www/datasink_auth.html",
        additional_context(request).update({
            'form': form,
        }),
        context_instance=RequestContext(request))


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
def job_create(request):
    extra_data = {
        'datasource_profile_id': request.session['datasource_profile_id'],
        'datasink_profile_id': request.session['datasink_profile_id'],
        'username': request.user.username,
        'key_ring': request.session['key_ring'],
    }
    
    form = JobCreateForm(request.POST or None, extra_data=extra_data)

    if form.is_valid():
        result = form.rest_save()
        if result:
            return redirect('index')

    return render_to_response(
        "www/job_create.html",
        additional_context(request).update({
            'form': form,
        }),
        context_instance=RequestContext(request))


@login_required
def job_log(request, job_id):
    rest_jobs = RestJobs(username=request.user.username)
    job_status = rest_jobs.get_job_status(job_id=job_id)
    
    rest_jobs = RestJobs(username=request.user.username)
    jobs = rest_jobs.get_all()
    
    job = get_job(jobs, job_id=job_id)
    
    rest_datasource_profile = RestDatasourceProfile(username=request.user.username)
    datasource_profiles = rest_datasource_profile.get_all()
    
    rest_datasink_profile = RestDatasinkProfile(username=request.user.username)
    datasink_profiles = rest_datasink_profile.get_all()
    
    job['datasinkTitle'] = get_sink_title(datasink_profiles, job['datasinkId'])
    job['datasources'] = []
    for source_id in job['datasourceIds']:
        job['datasources'].append({
            'id': source_id,
            'title': get_source_title(datasource_profiles, source_id)
        })
    
    return render_to_response(
        "www/job_log.html",
        {
            'job': job,
            'log': job_status['backupStatus'],
        },
        context_instance=RequestContext(request))
