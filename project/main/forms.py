# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from datetime import date, datetime
#from django.forms.widgets import CheckboxSelectMultiple

#from access.models import User
from remote_api.rest import RestDatasource, RestDatasourceProfile, RestDatasink, RestDatasinkProfile, RestJobs, RestAction, RestSearch

BACKUP_JOB_TIME_EXPRESSION = (
    ('realtime', _('now')),
    ('daily', _('daily')),
    ('weekly', _('weekly')),
    ('monthly', _('monthly')),
)


class DatasourceSelectForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        self.extra_data = kwargs.pop('extra_data')
        super(DatasourceSelectForm, self).__init__(*args, **kwargs)

        self.fields['datasource'] = forms.ChoiceField(label=_("Datasource"), widget=forms.RadioSelect, 
            choices=self.extra_data['datasource_choices'], required=False)

        if len(self.extra_data['datasource_profile_choices']):
            self.fields['datasource_profile'] = forms.ChoiceField(label=_("Datasource Profile"), required=False,
                choices=self.extra_data['datasource_profile_choices'], 
                help_text=_("Choose an existing data-source profile or select a new data-source below"))
    
    def clean(self):
        cleaned_data = super(DatasourceSelectForm, self).clean()
        datasource = cleaned_data.get("datasource", "")
        datasource_profile = cleaned_data.get("datasource_profile", "")
        
        if bool(datasource) != bool(datasource_profile):
            return cleaned_data
        else:
            raise forms.ValidationError("Please select a existing datasource profile, or create a new one by selecting a datasource.")


class DatasourceAuthForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        self.extra_data = kwargs.pop('extra_data')
        super(DatasourceAuthForm, self).__init__(*args, **kwargs)
        
        # add authentication form fields
        if self.extra_data['auth_data']['type'] == 'Input':
            # make sure 'requiredInputs' (= list of dicts) is sorted by 'order' dict value(s)
            self.extra_data['auth_data']['requiredInputs'] = sorted(self.extra_data['auth_data']['requiredInputs'], key=lambda k: k['order'])
            
            for item in self.extra_data['auth_data']['requiredInputs']:
                self.fields['input_key_%d' % item['order']] = forms.CharField(widget=forms.HiddenInput, initial=item['name'])
                
                field_kwargs = {
                    'label': _(item['label']),
                }
                
                if 'required' in item:
                    field_kwargs['required'] = item['required']
                else:
                    field_kwargs['required'] = False
                
                if 'description' in item:
                    field_kwargs['help_text'] = _(item['description'])
                
                if item['type'] == 'Password':
                    field_kwargs['widget'] = forms.PasswordInput
                    self.fields['input_value_%s' % item['order']] = forms.CharField(**field_kwargs)
                elif item['type'] == 'Bool':
                    self.fields['input_value_%s' % item['order']] = forms.BooleanField(**field_kwargs)
                else:
                    self.fields['input_value_%s' % item['order']] = forms.CharField(**field_kwargs)


class DatasinkSelectForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.extra_data = kwargs.pop('extra_data')
        super(DatasinkSelectForm, self).__init__(*args, **kwargs)

        self.fields['datasink'] = forms.ChoiceField(label=_("Datasink"), widget=forms.RadioSelect, choices=self.extra_data['datasink_choices'], required=False)
        
        if len(self.extra_data['datasink_profile_choices']):
            self.fields['datasink_profile'] = forms.ChoiceField(label=_("Datasink Profile"), choices=self.extra_data['datasink_profile_choices'], help_text=_("Choose an existing data-sink profile or select a new data-sink below"), required=False)
    
    def clean(self):
        cleaned_data = super(DatasinkSelectForm, self).clean()
        datasink = cleaned_data.get("datasink", "")
        datasink_profile = cleaned_data.get("datasink_profile", "")
        
        if bool(datasink) != bool(datasink_profile):
            return cleaned_data
        else:
            raise forms.ValidationError("Please select a existing datasink profile, or create a new one by selecting a datasink.")


class DatasinkAuthForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        self.extra_data = kwargs.pop('extra_data')
        super(DatasinkAuthForm, self).__init__(*args, **kwargs)
        
        # add authentication form fields
        if self.extra_data['auth_data']['type'] == 'Input':
            
            for item in self.extra_data['auth_data']['requiredInputs']:
                self.fields['input_key_%d' % item['order']] = forms.CharField(widget=forms.HiddenInput, initial=item['name'])
            
                field_kwargs = {
                    'label': _(item['label']),
                }
            
                if 'required' in item:
                    field_kwargs['required'] = item['required']
                else:
                    field_kwargs['required'] = False
            
                if item['type'] == 'Password':
                    field_kwargs['widget'] = forms.PasswordInput
            
                if 'description' in item:
                    field_kwargs['help_text'] = _(item['description'])
            
                self.fields['input_value_%s' % item['order']] = forms.CharField(**field_kwargs)


class JobDeleteForm(forms.Form):
    
    #confirm = forms.BooleanField(label=_("Ja, ich will das Backup löschen"), required=True)
    job_id = forms.CharField(label=_("Backup Name"), widget=forms.HiddenInput, required=True)
    
    def rest_save(self, username):
        rest_jobs = RestJobs(username=username)
        return rest_jobs.delete(job_id=self.cleaned_data['job_id'])


class JobEditForm(forms.Form):
    
    title = forms.CharField(label=_("Title"), required=True)
    time_expression = forms.ChoiceField(choices=BACKUP_JOB_TIME_EXPRESSION, initial='realtime', label=_("Interval"))
    
    def __init__(self, *args, **kwargs):
        self.extra_data = kwargs.pop('extra_data')
        kwargs['initial'] = {
            'title': self.extra_data['job']['jobTitle'],
            'time_expression': self.extra_data['job']['timeExpression'],
        }
        super(JobEditForm, self).__init__(*args, **kwargs)
        
        # datasource options
        job_datasource_options = self.extra_data['job']['sourceProfiles'][0]['options']
        
        for i, item in enumerate(self.extra_data['datasource_profile_options']):
            value = False
            for option in job_datasource_options:
                if option == item:
                    if job_datasource_options[option] == "true":
                        value = True
            
            self.fields['datasource_options_value_%s' % i] = forms.BooleanField(label=_(item), required=False, initial=value)
            self.fields['datasource_options_key_%s' % i] = forms.CharField(widget=forms.HiddenInput, initial=item)
        
        # actions
        for i, action in enumerate(self.extra_data['actions']):
	    if action.get('visibility', "") == "job":
            	self.fields['actions_value_%s' % i] = forms.BooleanField(label=_(action['title']), initial=action['checked'], required=False, help_text=_(action['description']))
            	self.fields['actions_key_%s' % i] = forms.CharField(widget=forms.HiddenInput, initial=action['actionId'])
    
    def field_group_job(self):
        return [
            self['title'],
            self['time_expression'],
        ]
    
    def field_group_datasource_options(self):
        return [field for field in self if field.name.startswith('datasource_options_value_')]

    def field_group_actions(self):
        return [field for field in self if field.name.startswith('actions_value_')]


class JobCreateForm(forms.Form):

    #key_ring = forms.CharField(label=_("Key Ring"), widget=forms.PasswordInput)
    
    title = forms.CharField(label=_("Title"), required=True)
    time_expression = forms.ChoiceField(choices=BACKUP_JOB_TIME_EXPRESSION, initial='realtime', label=_("Interval"))

    def __init__(self, *args, **kwargs):
        self.extra_data = kwargs.pop('extra_data')
        super(JobCreateForm, self).__init__(*args, **kwargs)
        
        rest_datasource_profile = RestDatasourceProfile(username=self.extra_data['username'])
        result = rest_datasource_profile.options(profile_id=self.extra_data['datasource_profile_id'], 
            data={'keyRing': self.extra_data['key_ring']})
        
        if result and 'sourceOptions' in result:
            for i, item in enumerate(result['sourceOptions']):
                self.fields['datasource_options_value_%s' % i] = forms.BooleanField(label=item, required=False)
                self.fields['datasource_options_key_%s' % i] = forms.CharField(widget=forms.HiddenInput, initial=item)
        
        rest_actions = RestAction()
        actions = rest_actions.get_all()
        
        for i, action in enumerate(actions):
            if action.get('visibility', "") == "job":
                action['options'] = rest_actions.options(action_id=action['actionId'])
            
                self.fields['actions_value_%d' % i] = forms.BooleanField(label=_(action['title']), required=False, help_text=_(action['description']))
                self.fields['actions_key_%d' % i] = forms.CharField(widget=forms.HiddenInput, initial=action['actionId'])
            
                for j, option in enumerate(action['options']):
                    self.fields['actions_value_%d_option_%d' % (i, j)] = forms.CharField(label=_(option), required=False)
                    self.fields['actions_key_%d_option_%d' % (i, j)] = forms.CharField(widget=forms.HiddenInput, initial=option)
    
    def field_group_job(self):
        return [
            self['title'],
            self['time_expression'],
        ]
    
    def field_group_datasource_options(self):
        return [field for field in self if field.name.startswith('datasource_options_value_')]

    def field_group_actions(self):
        return [field for field in self if field.name.startswith('actions_value_')]
    
    def rest_save(self):
        source_options = []
        actions = []
        
        data = {}
        
        for key in self.cleaned_data:
            
            if key.startswith('datasource_options_value_') and self.cleaned_data[key]:
                source_options.append(self.cleaned_data[key.replace('_value_', '_key_')])
            
            if key.startswith('actions_value_') and self.cleaned_data[key]:
                if '_option_' in key:
                    action_key = self.cleaned_data[key.split('_option_')[0].replace('_value_', '_key_')]
                    
                    option_key = action_key + '.' + self.cleaned_data[key.replace('_value_', '_key_')]
                    
                    option_value = self.cleaned_data[key]
                    data[option_key] = option_value
                else:
                    value = self.cleaned_data[key.replace('_value_', '_key_')]
                    actions.append(value)
                    if value == 'org.backmeup.encryption':
                        actions.append('org.backmeup.filesplitting')
        
        rest_jobs = RestJobs(username=self.extra_data['username'])
        
        data["keyRing"] = self.extra_data['key_ring']
        data['timeExpression'] = self.cleaned_data['time_expression']
        data['sourceProfiles'] = self.extra_data['datasource_profile_id']
        data['sinkProfileId'] = self.extra_data['datasink_profile_id']
        data['jobTitle'] = self.cleaned_data['title']
        data['actions'] = actions
        
        for item in source_options:
            params_key = str(data['sourceProfiles']) + "." + item
            data[params_key] = "true"
        
        job_result = rest_jobs.post(data=data)
        
        return job_result


class SearchForm(forms.Form):
    
    query = forms.CharField(label=_("Query"), required=True)
    
    def rest_save(self, username, key_ring):
        rest_search = RestSearch(username=username)
        result = rest_search.post({'query': self.cleaned_data['query'], 'keyRing': key_ring})
        return result


class SearchFilterForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        
        self.search_result = kwargs.pop('search_result')
        super(SearchFilterForm, self).__init__(*args, **kwargs)
        
        datasource_filter_choices = [("", "---"),]
        for item in self.search_result['bySource']:
            datasource_filter_choices.append((item['title'], _(item['title'])))
        
        self.fields['datasource_filter'] = forms.ChoiceField(label=_('Datasource Filter'), choices=datasource_filter_choices, required=False)
        
        type_filter_choices = [("", "---"),]
        for item in self.search_result['byType']:
		type_filter_choices.append((item['title'], _(item['title'])))	
	self.fields['type_filter'] = forms.ChoiceField(label=_('Type Filter'), choices=type_filter_choices, required=False)

	job_filter_choices = [("", "---"),]
	for item in self.search_result['byJob']:
	    time=_(item['title']).split(" ")[-1].replace(")", "").replace("(","")
            text=_(item['title']).split(" ")[:-1]
            datet=datetime.fromtimestamp(int(time)/1000)
            datet=datet.strftime("%d.%m.%Y %H:%M:%S")
            job_filter_choices.append((item['title'], "".join(text)+" ("+str(datet)+")"))
        
        self.fields['job_filter'] = forms.ChoiceField(label=_('Job Filter'), choices=job_filter_choices, required=False)
    
    def rest_save(self, search_id, username):
        rest_search = RestSearch(username=username)
        data = {}
        if self.cleaned_data['datasource_filter']:
            data['source'] = self.cleaned_data['datasource_filter']
        if self.cleaned_data['type_filter']:
            data['type'] = self.cleaned_data['type_filter']
	if self.cleaned_data['job_filter']:
	    data['job'] = self.cleaned_data['job_filter']
        result = rest_search.get(search_id=search_id, data=data)
        return result
