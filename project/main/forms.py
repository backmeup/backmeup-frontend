# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

#from access.models import User
from remote_api.rest import RestDatasource, RestDatasourceProfile


class DatasourceSelectForm(forms.Form):
    
    #datasource = forms.ChoiceField(label=_("Datasource"), widget=forms.RadioSelect)
    
    profile_name = forms.CharField(label=_("Backup Name"))
    
    key_ring = forms.CharField(label=_("Key Ring"), widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super(DatasourceSelectForm, self).__init__(*args, **kwargs)
        
        rest_datasource = RestDatasource()
        datasources = rest_datasource.get_all()

        choices = []
        
        for item in datasources:
            choices.append((item['datasourceId'], item['title']))
        
        self.fields['datasource'] = forms.ChoiceField(label=_("Datasource"), widget=forms.RadioSelect, choices=choices)
    
    def rest_save(self, username):
        rest_datasource_profile = RestDatasourceProfile(username=username)
        data = {
            "profile_name": self.cleaned_data['profile_name'],
            "key_ring": self.cleaned_data['key_ring'],
        }
        return rest_datasource_profile.auth(datasource_id=self.cleaned_data['datasource'], data=data)


class DatasourceAuthForm(forms.Form):
    
    key_ring = forms.CharField(label=_("Key Ring"), widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        auth_data = kwargs.pop('auth_data')
        super(DatasourceAuthForm, self).__init__(*args, **kwargs)
        
        if auth_data['type'] == 'Input':
            for i, item in enumerate(auth_data['typeMapping']):
                self.fields['input_key_%s' % i] = forms.CharField(widget=forms.HiddenInput, initial=item)
                
                field_kwargs = {
                    'label': _(item),
                }
                
                if not item in auth_data['requiredInputs']:
                    field_kwargs['required'] = False
                
                if auth_data['typeMapping'][item] == 'Password':
                    field_kwargs['widget'] = forms.PasswordInput
                
                self.fields['input_value_%s' % i] = forms.CharField(**field_kwargs)
    
    def rest_save(self, username, auth_data):
        rest_datasource_profile = RestDatasourceProfile(username=username)
        data = {
            "key_ring": self.cleaned_data['key_ring'],
        }
        for key in self.cleaned_data:
            if key.startswith('input_key_'):
                value = self.cleaned_data[key.replace('input_key_', 'input_value_')]
                data[key] = value
        
        return rest_datasource_profile.auth_post(profile_id=auth_data['profileId'], data=data)
        
        