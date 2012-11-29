# -*- coding: utf-8 -*-

import datetime

import re
import os
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper


from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
#from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _


from remote_api.rest import RestJobs, RestDatasourceProfile, RestDatasinkProfile, RestSearch, RestFile, RestUser, RestAction, RestDatasource
from main.forms import DatasourceSelectForm, DatasourceAuthForm
from main.forms import DatasinkSelectForm, DatasinkAuthForm
from main.forms import JobCreateForm, JobDeleteForm, JobEditForm
from main.forms import SearchForm, SearchFilterForm


def hasError(json_response):
    if 'errorType' in json_response:
        return True
    elif json_response.get('hasErrors', False):
        return True
    else:
        return False


def getErrorMsg(json_response):
    return _(json_response.get('errorMessage', json_response.get('errorType', 'Some error occurred.')))


def get_sink_title(sinks, sink_id):
    sink_id = int(sink_id)
    for sink in sinks:
        if sink['datasinkProfileId'] == sink_id:
            if 'identification' in sink:
                title = _(sink['pluginName'] + " - %(account)s") % {'account': sink['identification']}
            else:
                title = _(sink['title'])
            return title


def get_source_title(sources, source_id):
    source_id = int(source_id)
    for source in sources:
        if source['datasourceProfileId'] == source_id:
            if 'identification' in source:
                title = _(source['pluginName'] + " - %(account)s") % {'account': source['identification']}
            else:
                title = _(source['title'])
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
        profile = rest_datasource.get(request.session['datasource_profile_id'])
        if 'identification' in profile:
            title = _(profile['pluginName'] + " - %(account)s") % {'account': profile['identification']}
        else:
            title = profile['title']
        profile['good_title'] = title
        context['datasource_profile'] = profile

    if 'datasink_profile_id' in request.session:
        rest_datasink = RestDatasinkProfile(username=request.user.username)
        profile = rest_datasink.get(request.session['datasink_profile_id'])
        if 'identification' in profile:
            title = _(profile['pluginName'] + " - %(account)s") % {'account': profile['identification']}
        else:
            title = profile['title']
        profile['good_title'] = title
        context['datasink_profile'] = profile

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
                messages.error(request, _(jobs['errorMessage']))
                context['needs_email_validation'] = True
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
    try:
        del request.session['datasource_profile_id']
        del request.session['datasink_profile_id']
    except Exception:
        pass
    
    rest_datasource = RestDatasource()
    datasources = rest_datasource.get_all()
    datasource_choices = []
    for item in datasources:
        datasource_choices.append((item['datasourceId'], _(item['title'])))
    
    rest_datasource_profile = RestDatasourceProfile(username=request.user.username)
    datasource_profiles = rest_datasource_profile.get_all()
    datasource_profile_choices = []
    if len(datasource_profiles):
        for item in datasource_profiles:
            # no need to show profiles without 'identification'
            # * it's not a completely authenticated profile
            # * it's a profile whitch doesn't require authentication
            if 'identification' in item:
                title = _(item['pluginName'] + " - %(account)s") % {'account': item['identification']}
                datasource_profile_choices.append( (item['datasourceProfileId'], title) )
    if len(datasource_profile_choices):
        datasource_profile_choices = [("", "---")] + datasource_profile_choices
    
    extra_data = {
        'datasource_choices': datasource_choices,
        'datasource_profile_choices': datasource_profile_choices,
    }
    
    form = DatasourceSelectForm(request.POST or None, extra_data=extra_data)
    
    if form.is_valid():
        if form.cleaned_data['datasource']:
            rest_datasource_profile = RestDatasourceProfile(username=request.user.username)
            profile_name = _("%(plugin)s - profile") % {'plugin': form.cleaned_data['datasource']}
            data = {
                "profileName": profile_name,
                "keyRing": request.session['key_ring'],
            }
            result = rest_datasource_profile.auth(datasource_id=form.cleaned_data['datasource'], data=data)
            
            if hasError(result):
                messages.add_message(request, messages.ERROR, getErrorMsg(result))
            else:
                request.session['auth_data'] = result
                if result['type'] == 'OAuth':
                    request.session['next_step'] = 'datasource-auth'
                    return redirect(result['redirectURL'])
                return redirect('datasource-auth')

        elif form.cleaned_data['datasource_profile']:
            request.session['datasource_profile_id'] = form.cleaned_data['datasource_profile']
            try:
                del request.session['auth_data']
            except Exception:
                pass
            return redirect('datasink-select')
        
    context = additional_context(request)
    context['form'] = form

    return render_to_response(
        "www/datasource_select.html",
        context,
        context_instance=RequestContext(request))


@login_required
def datasource_auth(request):
    
    if request.session['auth_data']['type'] == 'Input':
        # make sure 'requiredInputs' (= list of dicts) is sorted by 'order' dict value(s)
        request.session['auth_data']['requiredInputs'] = sorted(request.session['auth_data']['requiredInputs'], key=lambda k: k['order'])
    
    extra_data = {
        'auth_data': request.session['auth_data'],
    }
    
    form = DatasourceAuthForm(request.POST or None, extra_data=extra_data)
    
    # redirect to next step if there is no authentication needed...
    # ... basically means auth type is 'Input' but there are noe input fields definded
    if not form.fields and request.session['auth_data']['type'] == 'Input':
        request.session['datasource_profile_id'] = request.session['auth_data']['profileId']
        return redirect('datasink-select')
    
    # the form won't be valid if auth type is OAuth
    # so form.is_valid() works for auth type Input only.
    if form.is_valid() or request.session['auth_data']['type'] == 'OAuth':
        data = {
            "keyRing": request.session['key_ring'],
        }
        
        if request.session['auth_data']['type'] == 'Input':
            for key in form.cleaned_data:
                if key.startswith('input_key_'):
                    value = form.cleaned_data[key.replace('input_key_', 'input_value_')]
                    data[form.cleaned_data[key]] = value
        elif request.session['auth_data']['type'] == 'OAuth':
            data.update(request.session['auth_data']['oauth_data'])
        
        # add authentication data to newly created datasource profile
        rest_datasource_profile = RestDatasourceProfile(username=request.user.username)
        result = rest_datasource_profile.auth_post(profile_id=request.session['auth_data']['profileId'], data=data)
        
        if hasError(result):
            del request.session['auth_data']
            messages.add_message(request, messages.ERROR, getErrorMsg(result))
            return redirect('datasource-select')
        else:
            request.session['datasource_profile_id'] = request.session['auth_data']['profileId']
            del request.session['auth_data']
            return redirect('datasink-select')
    
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

    if not form.fields and request.session['auth_data']['type'] == 'Input':
        request.session['datasink_profile_id'] = request.session['auth_data']['profileId']
        return redirect('job-create')

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
def job_edit(request, job_id):
    rest_jobs = RestJobs(username=request.user.username)
    job = rest_jobs.get(job_id=job_id)
    
    datasource_profile_id = job['sourceProfiles'][0]['id']
    datasink_profile_id = job['sinkProfileId']
    
    rest_datasource_profile = RestDatasourceProfile(username=request.user.username)
    datasource_profile_options = rest_datasource_profile.options(profile_id=datasource_profile_id, 
        data={'keyRing': request.session['key_ring']})['sourceOptions']
    
    rest_actions = RestAction()
    actions = rest_actions.get_all()
    
    for action in actions:
        action['options'] = rest_actions.options(action_id=action['actionId'])
        action['checked'] = False
        
        for job_action in job['actions']:
            if job_action['id'] == action['actionId']:
                action['checked'] = True
    
    extra_data = {
        'job': job,
        'datasource_profile_options': datasource_profile_options,
        'actions': actions,
    }
    
    form = JobEditForm(request.POST or None, extra_data=extra_data)
    
    if form.is_valid():
        new_source_options = []
        new_actions = []

        for key in form.cleaned_data:

            if key.startswith('datasource_options_value_') and form.cleaned_data[key]:
                new_source_options.append(form.cleaned_data[key.replace('_value_', '_key_')])

            if key.startswith('actions_value_') and form.cleaned_data[key]:
                value = form.cleaned_data[key.replace('_value_', '_key_')]
                new_actions.append(value)

        rest_jobs = RestJobs(username=request.user.username)
        data = {
            "keyRing": request.session['key_ring'],
            'timeExpression': form.cleaned_data['time_expression'],
            'sourceProfiles': datasource_profile_id,
            'sinkProfileId': datasink_profile_id,
            'jobTitle': form.cleaned_data['title'],
            'actions': new_actions,
        }
        for item in new_source_options:
            params_key = str(data['sourceProfiles']) + "." + item
            data[params_key] = "true"
        job_result = rest_jobs.put(job_id=job_id ,data=data)
        if hasError(job_result):
            messages.add_message(request, messages.ERROR, getErrorMsg(job_result))
        else:
            return redirect('index')
    
    return render_to_response("www/job_edit.html", {
        'form': form,
    }, context_instance=RequestContext(request))


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


@login_required
def zip_files(request):
    rest_user = RestUser(username=request.user.username)
    user = rest_user.get()
    user_id = int(user['userId'])
    
    file_list = [f for f in os.listdir(settings.ZIP_ARCHIVES_PATH % user_id) if re.match(settings.ZIP_ARCHIVES_MATCH_PATTERN, f)]
    return render_to_response('www/zip_file_list.html', {
        'file_list': file_list,
    }, context_instance=RequestContext(request))


@login_required
def zip_download(request):
    """
    Send a file through Django without loading the whole file into
    memory at once. The FileWrapper will turn the file object into an
    iterator for chunks of 8KB.
    
    (performance might be improved by using apache mod_xsendfile.)
    """
    rest_user = RestUser(username=request.user.username)
    user = rest_user.get()
    user_id = int(user['userId'])
    
    filename = settings.ZIP_ARCHIVES_PATH % user_id
    filename = filename + request.GET['f']
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=' + request.GET['f']
    response['Content-Length'] = os.path.getsize(filename)
    return response

