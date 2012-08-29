# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

#from access.models import User
from remote_api.rest import RestDatasource, RestDatasourceProfile, RestDatasink, RestDatasinkProfile


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
        self.auth_data = kwargs.pop('auth_data')
        super(DatasourceAuthForm, self).__init__(*args, **kwargs)
        
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
    
    def rest_save(self, username):
        rest_datasource_profile = RestDatasourceProfile(username=username)
        data = {
            "keyRing": self.cleaned_data['key_ring'],
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
    
    profile_name = forms.CharField(label=_("Backup Name"))
    
    key_ring = forms.CharField(label=_("Key Ring"), widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super(DatasinkSelectForm, self).__init__(*args, **kwargs)
        
        rest_datasink = RestDatasink()
        datasinks = rest_datasink.get_all()

        choices = []
        
        for item in datasinks:
            choices.append((item['datasinkId'], item['title']))
        
        self.fields['datasink'] = forms.ChoiceField(label=_("Datasink"), widget=forms.RadioSelect, choices=choices)
    
    def rest_save(self, username):
        rest_datasink_profile = RestDatasinkProfile(username=username)
        data = {
            "profile_name": self.cleaned_data['profile_name'],
            "key_ring": self.cleaned_data['key_ring'],
        }
        return rest_datasink_profile.auth(datasink_id=self.cleaned_data['datasink'], data=data)


class DatasinkAuthForm(forms.Form):
    
    key_ring = forms.CharField(label=_("Key Ring"), widget=forms.PasswordInput)
    
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
            
    def rest_save(self, username):
        rest_datasink_profile = RestDatasinkProfile(username=username)
        data = {
            "key_ring": self.cleaned_data['key_ring'],
        }
        if self.auth_data['type'] == 'Input':
            for key in self.cleaned_data:
                if key.startswith('input_key_'):
                    value = self.cleaned_data[key.replace('input_key_', 'input_value_')]
                    data[self.cleaned_data[key]] = value
        elif self.auth_data['type'] == 'OAuth':
            data.update(self.auth_data['oauth_data'])
        return rest_datasink_profile.auth_post(profile_id=self.auth_data['profileId'], data=data)
