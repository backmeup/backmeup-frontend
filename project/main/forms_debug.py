# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import CheckboxSelectMultiple

#from access.models import User
from remote_api.rest import RestDatasource, RestDatasourceProfile, RestDatasink, RestDatasinkProfile, RestJobs


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