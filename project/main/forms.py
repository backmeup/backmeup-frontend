# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
#from django.forms.widgets import CheckboxSelectMultiple

#from access.models import User
from remote_api.rest import RestDatasource, RestDatasourceProfile, RestDatasink, RestDatasinkProfile, RestJobs, RestAction

BACKUP_JOB_TIME_EXPRESSION = (
    ('realtime', _('now')),
    ('daily', _('daily')),
    ('weekly', _('weekly')),
    ('monthly', _('monthly')),
)


class DatasourceSelectForm(forms.Form):

    #datasource = forms.ChoiceField(label=_("Datasource"), widget=forms.RadioSelect)
    #profile_name = forms.CharField(label=_("Backup Name"))
    #key_ring = forms.CharField(label=_("Key Ring"), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(DatasourceSelectForm, self).__init__(*args, **kwargs)

        rest_datasource = RestDatasource()
        datasources = rest_datasource.get_all()

        choices = []

        for item in datasources:
            choices.append((item['datasourceId'], _(item['title'])))
        
        self.fields['datasource'] = forms.ChoiceField(label=_("Datasource"), widget=forms.RadioSelect, choices=choices)

    def rest_save(self, username, key_ring):
        rest_datasource_profile = RestDatasourceProfile(username=username)
        profile_name = _("%(plugin)s - profile") % {'plugin': self.cleaned_data['datasource']}
        data = {
            "profile_name": profile_name,
            "key_ring": key_ring,
        }
        return rest_datasource_profile.auth(datasource_id=self.cleaned_data['datasource'], data=data)


class DatasourceAuthForm(forms.Form):

    #key_ring = forms.CharField(label=_("Key Ring"), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.auth_data = kwargs.pop('auth_data')
        self.username = kwargs.pop('username')
        super(DatasourceAuthForm, self).__init__(*args, **kwargs)
        
        # add authentication form fields
        if self.auth_data['type'] == 'Input':
            for i, item in enumerate(self.auth_data['typeMapping']):
                self.fields['input_key_%s' % i] = forms.CharField(widget=forms.HiddenInput, initial=item)

                field_kwargs = {
                    'label': _(item),
                }

                if not item in self.auth_data['requiredInputs']:
                    field_kwargs['required'] = False

                if self.auth_data['typeMapping'][item] == 'Password':
                    field_kwargs['widget'] = forms.PasswordInput

                self.fields['input_value_%s' % i] = forms.CharField(**field_kwargs)
        
    def rest_save(self, username, key_ring):
        rest_datasource_profile = RestDatasourceProfile(username=username)
        data = {
            "keyRing": key_ring,
        }
        if self.auth_data['type'] == 'Input':
            for key in self.cleaned_data:
                if key.startswith('input_key_'):
                    value = self.cleaned_data[key.replace('input_key_', 'input_value_')]
                    data[self.cleaned_data[key]] = value
        elif self.auth_data['type'] == 'OAuth':
            data.update(self.auth_data['oauth_data'])
        return rest_datasource_profile.auth_post(profile_id=self.auth_data['profileId'], data=data)


class DatasinkSelectForm(forms.Form):

    #datasink = forms.ChoiceField(label=_("Datasink"), widget=forms.RadioSelect)
    #profile_name = forms.CharField(label=_("Backup Name"))
    #key_ring = forms.CharField(label=_("Key Ring"), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(DatasinkSelectForm, self).__init__(*args, **kwargs)

        rest_datasink = RestDatasink()
        datasinks = rest_datasink.get_all()

        choices = []

        for item in datasinks:
            choices.append((item['datasinkId'], item['title']))

        self.fields['datasink'] = forms.ChoiceField(label=_("Datasink"), widget=forms.RadioSelect, choices=choices)

    def rest_save(self, username, key_ring):
        rest_datasink_profile = RestDatasinkProfile(username=username)
        profile_name = _("%(plugin)s - profile") % {'plugin': self.cleaned_data['datasink']}
        data = {
            "profile_name": profile_name,
            "key_ring": key_ring,
        }
        return rest_datasink_profile.auth(datasink_id=self.cleaned_data['datasink'], data=data)


class DatasinkAuthForm(forms.Form):

    #key_ring = forms.CharField(label=_("Key Ring"), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.auth_data = kwargs.pop('auth_data')
        super(DatasinkAuthForm, self).__init__(*args, **kwargs)

        if self.auth_data['type'] == 'Input':
            for i, item in enumerate(self.auth_data['typeMapping']):
                self.fields['input_key_%s' % i] = forms.CharField(widget=forms.HiddenInput, initial=item)

                field_kwargs = {
                    'label': _(item),
                }

                if not item in self.auth_data['requiredInputs']:
                    field_kwargs['required'] = False

                if self.auth_data['typeMapping'][item] == 'Password':
                    field_kwargs['widget'] = forms.PasswordInput

                self.fields['input_value_%s' % i] = forms.CharField(**field_kwargs)

    def rest_save(self, username, key_ring):
        rest_datasink_profile = RestDatasinkProfile(username=username)
        data = {
            "keyRing": key_ring,
        }
        if self.auth_data['type'] == 'Input':
            for key in self.cleaned_data:
                if key.startswith('input_key_'):
                    value = self.cleaned_data[key.replace('input_key_', 'input_value_')]
                    data[self.cleaned_data[key]] = value
        elif self.auth_data['type'] == 'OAuth':
            data.update(self.auth_data['oauth_data'])
        return rest_datasink_profile.auth_post(profile_id=self.auth_data['profileId'], data=data)


class JobDeleteForm(forms.Form):
    
    confirm = forms.BooleanField(label=_("Ja, ich will das Backup löschen"), required=True)
    job_id = forms.CharField(label=_("Backup Name"), widget=forms.HiddenInput, required=True)
    
    def rest_save(self, username):
        rest_jobs = RestJobs(username=username)
        
        return rest_jobs.delete(job_id=self.cleaned_data['job_id'])


class JobCreateForm(forms.Form):

    #key_ring = forms.CharField(label=_("Key Ring"), widget=forms.PasswordInput)
    
    title = forms.CharField(label=_("Title"), required=True)
    time_expression = forms.ChoiceField(choices=BACKUP_JOB_TIME_EXPRESSION, initial='realtime')

    def __init__(self, *args, **kwargs):
        self.extra_data = kwargs.pop('extra_data')
        super(JobCreateForm, self).__init__(*args, **kwargs)
        
        # rest_datasource_profile = RestDatasourceProfile(username=self.username)
        #         datasource_profiles = rest_datasource_profile.get_all()
        # 
        #         datasource_profile_choices = []
        # 
        #         for item in datasource_profiles:
        #             datasource_profile_choices.append((str(item['datasourceProfileId']), item['title']))
        # 
        #         self.fields['datasource_profile'] = forms.MultipleChoiceField(label=_("Datasource Profile"), widget=CheckboxSelectMultiple, choices=datasource_profile_choices)
        # 
        # 
        #         rest_datasink_profile = RestDatasinkProfile(username=self.username)
        #         datasink_profiles = rest_datasink_profile.get_all()
        # 
        #         datasink_profile_choices = []
        # 
        #         for item in datasink_profiles:
        #             datasink_profile_choices.append((str(item['datasinkProfileId']), item['title']))
        # 
        #         self.fields['datasink_profile'] = forms.MultipleChoiceField(label=_("Datasink Profile"), widget=CheckboxSelectMultiple, choices=datasink_profile_choices)
        
        rest_datasource_profile = RestDatasourceProfile(username=self.extra_data['username'])
        result = rest_datasource_profile.options(profile_id=self.extra_data['datasource_profile_id'], 
            data={'key_ring': self.extra_data['key_ring']})
        
        if result and 'sourceOptions' in result:
            for i, item in enumerate(result['sourceOptions']):
                self.fields['datasource_options_value_%s' % i] = forms.BooleanField(label=item, required=False)
                self.fields['datasource_options_key_%s' % i] = forms.CharField(widget=forms.HiddenInput, initial=item)
        
        rest_actions = RestAction()
        actions = rest_actions.get_all()
        
        for i, action in enumerate(actions):
            action['options'] = rest_actions.options(action_id=action['actionId'])
            
            self.fields['actions_value_%s' % i] = forms.BooleanField(label=_(action['title']), required=False, help_text=_(action['description']))
            self.fields['actions_key_%s' % i] = forms.CharField(widget=forms.HiddenInput, initial=action['actionId'])
            
            # action options are just dummy yet
            #for j, option in enumerate(action['options']):
            #    self.fields['action_options_value_%s_%s' % (i, j)] = forms.BooleanField(label=_(option), required=False)
            #    self.fields['action_options_key_%s_%s' % (i, j)] = forms.CharField(widget=forms.HiddenInput, initial=option)
    
    def field_group_job(self):
        return return [
            self['title'],
            self['time_expression'],
        ]
    
    def field_group_datasource_options(self):
        return [field for field in self if field.name.startswith('datasource_options_value_')]

    def field_group_actions(self):
        return [field for field in self if field.name.startswith('actions_value_')]

    def rest_save(self):
        source_options = ''
        actions = []
        
        for key in self.cleaned_data:
            
            if key.startswith('datasource_options_value_') and self.cleaned_data[key]:
                value = self.cleaned_data[key.replace('_value_', '_key_')]
                source_options = '%s"%s",' % (source_options, value)
            
            if key.startswith('actions_value_') and self.cleaned_data[key]:
                value = self.cleaned_data[key.replace('_value_', '_key_')]
                actions.append(value)
        
        rest_jobs = RestJobs(username=self.extra_data['username'])
        data = {
            "key_ring": self.extra_data['key_ring'],
            'time_expression': self.cleaned_data['time_expression'],
            'source_profile_ids': self.extra_data['datasource_profile_id'],
            'sink_profile_ids': self.extra_data['datasink_profile_id'],
            'title': self.cleaned_data['title'],
            'actions': actions,
        }
        job_result = rest_jobs.post(data=data)
        
        rest_datasource_profile = RestDatasourceProfile(username=self.extra_data['username'])
        data = {
            "keyRing": self.extra_data['key_ring'],
        }
        
        
        print "####actions:", actions
        
        datasource_options_result = rest_datasource_profile.put(profile_id=self.extra_data['datasource_profile_id'], 
            job_id=job_result['jobId'], source_options=source_options)
        
        #for key in self.cleaned_data
        
        #
        # actions!!!
        #
        
        return {
            'job': job_result,
            'datasource_options': datasource_options_result,
        }