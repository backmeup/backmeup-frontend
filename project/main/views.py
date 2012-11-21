# -*- coding: utf-8 -*-

import datetime


from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
#from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _


from remote_api.rest import RestJobs, RestDatasourceProfile, RestDatasinkProfile, RestSearch, RestFile
from main.forms import DatasourceSelectForm, DatasourceAuthForm
from main.forms import DatasinkSelectForm, DatasinkAuthForm
from main.forms import JobCreateForm, JobDeleteForm
from main.forms import SearchForm, SearchFilterForm


def get_sink_title(sinks, sink_id):
    sink_id = int(sink_id)
    for sink in sinks:
        if sink['datasinkProfileId'] == sink_id:
            if 'identification' in sink:
                title = _(sink['pluginName'] + " - %(account)s") % {'account': sink['identification']}
            else:
                title = sink['title']
            return title


def get_source_title(sources, source_id):
    source_id = int(source_id)
    for source in sources:
        if source['datasourceProfileId'] == source_id:
            if 'identification' in source:
                title = _(source['pluginName'] + " - %(account)s") % {'account': source['identification']}
            else:
                title = source['title']
            return title
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
        rest_datasink = RestDatasinkProfile(username=request.user.username)
        context['datasink_profile'] = rest_datasink.get(request.session['datasink_profile_id'])
    
    context['search_form'] = SearchForm(request.POST or None)
    
    return context


def index(request):
    context = additional_context(request)
    if request.user.is_authenticated():
        
        ### delete job form start
        job_delete_form = JobDeleteForm(request.POST or None)
        if job_delete_form.is_valid():
            result = job_delete_form.rest_save(username=request.user.username)
            if result:
                messages.add_message(request, messages.SUCCESS, _(u'Backup was successfully deleted.'))
            else:
                messages.add_message(request, messages.ERROR, _(u'Backup couldn\'t be deleted.'))
        context['job_delete_form'] = job_delete_form
        
        rest_jobs = RestJobs(username=request.user.username)
        jobs = rest_jobs.get_all()
        #### delete job form end

        if jobs and 'errorType' in jobs:
            if jobs['errorType'] == 'org.backmeup.model.exceptions.UnknownUserException':
                logout(request)
                redirect('index')
            else:
                messages.error(request, _(jobs['errorType']))
        else:
            rest_datasource_profile = RestDatasourceProfile(username=request.user.username)
            datasource_profiles = rest_datasource_profile.get_all()
            
            rest_datasink_profile = RestDatasinkProfile(username=request.user.username)
            datasink_profiles = rest_datasink_profile.get_all()
            
            for job in jobs:
                # need to cut of first 3 numbers to get valid unix timestamp
                if 'createDate' in job:
                    job['createDate'] = datetime.datetime.fromtimestamp(job['createDate']/1000)
                if 'startDate' in job:
                    job['startDate'] = datetime.datetime.fromtimestamp(job['startDate']/1000)
                if 'lastBackup' in job:
                    job['lastBackup'] = datetime.datetime.fromtimestamp(job['lastBackup']/1000)
                if 'nextBackup' in job:
                    job['nextBackup'] = datetime.datetime.fromtimestamp(job['nextBackup']/1000)
                
                job['datasink']['title'] = get_sink_title(datasink_profiles, job['datasink']['datasinkId'])
                #job['datasources'] = []
                for datasource in job['datasources']:
                    datasource['title'] = get_source_title(datasource_profiles, datasource['datasourceId'])
            context['jobs'] = jobs
    
    return render_to_response(
        "www/index.html",
        context,
        context_instance=RequestContext(request))


@login_required
def datasource_select(request):
    form = DatasourceSelectForm(request.POST or None, username=request.user.username)
    if form.is_valid():
        #request.session['key_ring'] = form.cleaned_data['key_ring']
        auth_data = form.rest_save(username=request.user.username, key_ring=request.session['key_ring'])
        if isinstance(auth_data, int):
            request.session['datasource_profile_id'] = auth_data
            try:
                del request.session['auth_data']
            except Exception:
                pass
            return redirect('datasink-select')
        else:
            request.session['auth_data'] = auth_data
            if auth_data['type'] == 'OAuth':
                request.session['next_step'] = 'datasource-auth'
                return redirect(auth_data['redirectURL'])
            return redirect('datasource-auth')
    
    context = additional_context(request)
    context['form'] = form
    
    return render_to_response(
        "www/datasource_select.html",
        context,
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
        else:
            del request.session['auth_data']
            messages.add_message(request, messages.ERROR, 'Some error occured.')
            return redirect(datasource_select)
    
    context = additional_context(request)
    context['form'] = form
    
    return render_to_response(
        "www/datasource_auth.html",
        context,
        context_instance=RequestContext(request))


@login_required
def datasink_select(request):
    form = DatasinkSelectForm(request.POST or None, username=request.user.username)
    if form.is_valid():
        #request.session['key_ring'] = form.cleaned_data['key_ring']
        auth_data = form.rest_save(username=request.user.username, key_ring=request.session['key_ring'])
        if isinstance(auth_data, int):
            request.session['datasink_profile_id'] = auth_data
            try:
                del request.session['auth_data']
            except Exception:
                pass
            return redirect('job-create')
        else:
            request.session['auth_data'] = auth_data
            if auth_data['type'] == 'OAuth':
                request.session['next_step'] = 'datasink-auth'
                return redirect(auth_data['redirectURL'])
            return redirect('datasink-auth')
    
    context = additional_context(request)
    context['form'] = form
    
    return render_to_response(
        "www/datasink_select.html",
        context,
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
        if not result == False:
            request.session['datasink_profile_id'] = request.session['auth_data']['profileId']
            try:
                del request.session['auth_data']
            except Exception:
                pass
            return redirect('job-create')
        else:
            del request.session['auth_data']
            messages.add_message(request, messages.ERROR, 'Some error occured.')
            return redirect(datasink_select)
    
    context = additional_context(request)
    context['form'] = form
    
    return render_to_response(
        "www/datasink_auth.html",
        context,
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

    context = additional_context(request)
    context['form'] = form
    return render_to_response(
        "www/job_create.html",
        context,
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
    
    job['datasink']['title'] = get_sink_title(datasink_profiles, job['datasink']['datasinkId'])
    #job['datasources'] = []
    for datasource in job['datasources']:
        datasource['title'] = get_source_title(datasource_profiles, datasource['datasourceId'])
    
    context = {
        'job': job,
        'log': job_status['backupStatus'],
    }
    try:
        context['current_status'] = job_status['backupStatus'][0]['type']
    except:
        pass
    
    return render_to_response(
        "www/job_log.html",
        context,
        context_instance=RequestContext(request))


@login_required
def search(request):
    form = SearchForm(request.POST or None)
    
    if form.is_valid():
        result = form.rest_save(request.user.username, request.session['key_ring'])
        return redirect('search-result', search_id=result['searchId'])
    
    referer = request.META.get('HTTP_REFERER', 'index')
    
    return redirect(referer)


@login_required
def search_result(request, search_id):
    
    rest_search = RestSearch(username=request.user.username)
    result = rest_search.get(search_id)
    
    try:
        for item in result['files']:
            item['timeStamp'] = datetime.datetime.fromtimestamp(item['timeStamp']/1000)
            item['simple_type'] = item['type'].split('/')[0]
    except Exception:
        pass
    
    form = SearchFilterForm(request.POST or None, search_result=result)
    
    if form.is_valid():
        new_result = form.rest_save(search_id=search_id, username=request.user.username)
        result = new_result
    
    return render_to_response('www/search_result.html', {
        'result': result,
        'search_id': search_id,
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def file_info(request, search_id, file_id):
    
    rest_file = RestFile(username=request.user.username)
    result = rest_file.get(file_id=file_id)
    
    result['details']['fileInfo']['timeStamp'] = datetime.datetime.fromtimestamp(int(result['details']['fileInfo']['timeStamp'])/1000)
    result['details']['fileInfo']['filename'] = result['details']['fileInfo']['path'].split('/')[-1]
    return render_to_response('www/search_result_detail.html', {
        'file': result['details']['fileInfo'],
        'search_id': search_id,
    }, context_instance=RequestContext(request))
    