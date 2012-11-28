# -*- coding: utf-8 -*-

import json
import requests

from django.conf import settings

# TODO
# move all requests api specific code to RestBase


class RestBase(object):
    u'''
    To abstract the requests api
    '''

    def __init__(self, url=settings.REST_API_BASE_URL):
        self.base_url = url

    def _delete(self, path="", data=None):
        try:
            response = requests.delete(self.base_url + path, data=data)
        except Exception as e:
            return False
        if settings.DEBUG:
            print "... DELETE ..."
            print "####### url:", self.base_url + path
            print "###### data:", data
            print "########### response"
            print "#### status:", response.status_code
            print "###### json:", json.dumps(response.json, indent=2)
            print "............................."
        return response

    def _get(self, path="", data=None):
        try:
            response = requests.get(self.base_url + path, data=data)
        except Exception as e:
            return False
        if settings.DEBUG:
            print "... GET ..."
            print "####### url:", self.base_url + path
            print "###### data:", data
            print "########### response"
            print "#### status:", response.status_code
            print "###### json:", json.dumps(response.json, indent=2)
            print "............................."
        if response.status_code == 204:
            return True
        else:
            return response.json

    def _post(self, path="", data=None):
        try:
            response = requests.post(self.base_url + path, data=data)
        except Exception as e:
            return False
        if settings.DEBUG:
            print "... POST ..."
            print "####### url:", self.base_url + path
            print "###### data:", data
            print "########### response"
            print "#### status:", response.status_code
            print "###### json:", json.dumps(response.json, indent=2)
            print "............................."
        if response.status_code == 204:
            return True
        elif response.status_code == 400 or response.status_code == 404 or response.status_code == 401:
            return False
        return response.json

    def _put(self, path="", data=None):
        try:
            response = requests.put(self.base_url + path, data=data)
        except Exception as e:
            return False
        if settings.DEBUG:
            print "... PUT ..."
            print "####### url:", self.base_url + path
            print "###### data:", data
            print "########### response"
            print "#### status:", response.status_code
            print "###### json:", json.dumps(response.json, indent=2)
            print "............................."
        if response.status_code == 204:
            return True
        return response.json


class RestUser(RestBase):
    '''
    crud + "check login" methods for user accounts
    '''

    def __init__(self, username, path="users/"):
        if not username:
            raise ValueError('argument "username" is missing.')
        self.username = username

        super(RestUser, self).__init__()
        self.base_url = "%s%s%s/" % (self.base_url, path, self.username)

    def delete(self):
        '''
        delete user
        '''
        return self._delete()

    def get(self):
        '''
        get user data or check if user exists
        '''
        return self._get()

    def post(self, data):
        '''
        create/register/signup user
        '''
        if not data:
            raise ValueError('argument "data" is missing.')
        # validate?
        req_params = {
            'password': data['password'],
            'keyRing': data['keyRing'],
            'email': data['email'],
        }
        return self._post('register', req_params)

    def put(self, data):
        '''
        change user data
        '''
        if not data:
            raise ValueError('argument "data" is missing.')
        # validate?

        req_params = {}
        if not 'old_password' in data:
            raise ValueError('argument "data[\'old_password\']" is missing.')
        req_params['oldPassword'] = data['old_password']

        if 'password' in data:
            req_params['password'] = data['password']
        if 'keyRing' in data:
            req_params['keyRing'] = data['keyRing']
        if 'email' in data:
            req_params['email'] = data['email']
        if 'username' in data:
            req_params['username'] = data['username']

        return self._put(data=req_params)

    def check_login(self, password):
        '''
        checks if user-password combination is valid to login.

        the actual login and session handling is done by the backmeup-frontend.
        '''
        if not password:
            raise ValueError('argument "password" is missing.')

        req_params = {
            'password': password,
        }

        return self._post(path='login/', data=req_params)


class RestEmailVerification(RestBase):

    def __init__(self, path="users/"):
        super(RestEmailVerification, self).__init__()
        self.base_url = self.base_url + path

    def verify(self, hash):
        return self._get(path="%s/verifyEmail" % hash)
    
    def resend(self, username):
        return self._get(path="%s/newVerificationEmail" % username)


class RestDatasource(RestBase):

    def __init__(self, path="datasources/"):
        super(RestDatasource, self).__init__()
        self.base_url = self.base_url + path

    def get_all(self):
        result = self._get()
        
        if result and 'sources' in result:
            return result['sources']
        else:
            return result

    def post(self, data):
        return self._post(data=data)

    def delete(self, datasource_id):
        return self._delete(path=datasource_id)


class RestDatasourceProfile(RestBase):

    def __init__(self, username, path="datasources/"):
        if not username:
            raise ValueError('argument "username" is missing.')
        self.username = username

        super(RestDatasourceProfile, self).__init__()
        self.base_url = "%s%s%s/" % (self.base_url, path, self.username)
    
    def get(self, profile_id):
        profile_id = int(profile_id)
        for profile in self.get_all():
            if profile['datasourceProfileId'] == profile_id:
                return profile
    
    def get_all(self):
        result = self._get(path="profiles/")
        
        if result and 'sourceProfiles' in result:
            return result['sourceProfiles']
        else:
            return result

    def delete(self, profile_id):
        if not profile_id:
            raise ValueError('argument "profile_id" is missing.')
        return self._delete(path="profiles/" + profile_id)

    def options(self, profile_id, data):
        if not profile_id:
            raise ValueError('argument "profile_id" is missing.')
        if not "key_ring" in data:
            raise ValueError('key "key_ring is missing in argument "data".')
        
        params = {
            "keyRing": data['key_ring'],
        }
        profile_id = str(profile_id)
        return self._post(path="profiles/" + profile_id + "/options", data=params)

    def put(self, profile_id, job_id, source_options):
        #if not profile_id:
        #    raise ValueError('argument "profile_id" is missing.')
        #if not source_options:
        #    raise ValueError('argument "source_options" is missing.')

        data = {
            "sourceOptions": source_options,
        }
        return self._put(path="profiles/" + profile_id + "/" + str(job_id), data=data)

    def auth(self, datasource_id, data):
        if not "profile_name" in data:
            raise ValueError('key "profile_name is missing in argument "data".')
        if not "key_ring" in data:
            raise ValueError('key "key_ring is missing in argument "data".')
        params = {
            "profileName": data["profile_name"],
            "keyRing": data["key_ring"],
        }
        return self._post(path="%s/auth" % datasource_id, data=params)

    def auth_post(self, profile_id, data):
        #if not "key_ring" in data:
        #    raise ValueError('key "key_ring" is missing in argument "data".')
        return self._post(path="%s/auth/post" % profile_id, data=data)


class RestDatasink(RestBase):

    def __init__(self, path='datasinks/'):
        super(RestDatasink, self).__init__()
        self.base_url = self.base_url + path

    def get_all(self):
        result = self._get()
        
        if result and 'sinks' in result:
            return result['sinks']
        else:
            return

    def post(self, data):
        return self._post(data)

    def delete(self, datasink_id):
        return self._delete(path=datasink_id)


class RestDatasinkProfile(RestBase):

    def __init__(self, username, path="datasinks/"):
        if not username:
            raise ValueError('argument "username" is missing.')
        self.username = username

        super(RestDatasinkProfile, self).__init__()
        self.base_url = "%s%s%s/" % (self.base_url, path, self.username)
    
    def get(self, profile_id):
        profile_id = int(profile_id)
        for profile in self.get_all():
            if profile['datasinkProfileId'] == profile_id:
                return profile
    
    def get_all(self):
        result = self._get(path="profiles/")
        
        if result and 'sinkProfiles' in result:
            return result['sinkProfiles']
        else:
            return result
        
    def delete(self, profile_id):
        return self._delete(path="profiles/" + profile_id)

    def auth(self, datasink_id, data):
        if not "profile_name" in data:
            raise ValueError('key "profile_name" is missing in argument "data".')
        if not "key_ring" in data:
            raise ValueError('key "key_ring" is missing in argument "data".')
        params = {
            "profileName": data["profile_name"],
            "keyRing": data["key_ring"],
        }
        return self._post(path="%s/auth" % datasink_id, data=params)

    def auth_post(self, profile_id, data):
        #if not "key_ring" in data:
        #    raise ValueError('key "key_ring is missing in argument "data".')
        return self._post(path="%s/auth/post" % profile_id, data=data)


class RestAction(RestBase):

    def __init__(self, path="actions/"):
        super(RestAction, self).__init__()
        self.base_url = self.base_url + path

    def get_all(self):
        result = self._get()
        
        if result and 'actions' in result:
            return result['actions']
        else:
            return result
    
    def options(self, action_id):
        result = self._get(path=action_id + "/options/")
        
        if result and 'actionOptions' in result:
            return result['actionOptions']
        else:
            return result
    
    def post(self, data):
        if not "name" in data:
            raise ValueError('key "name" is missing in argument "data".')
        if not "filename" in data:
            raise ValueError('key "filename" is missing in argument "data".')

        params = {
            'name': data['name'],
            'filename': data['filename'],
        }

        return self._post(data=params)

    def delete(self, action_id):
        return self._delete(path=action_id + "/")


class RestJobs(RestBase):

    def __init__(self, username, path="jobs/"):
        if not username:
            raise ValueError('argument "username" is missing.')
        self.username = username

        super(RestJobs, self).__init__()
        self.base_url = "%s%s%s/" % (self.base_url, path, self.username)

    def post(self, data):
        """
        sourceProfileIds - Die zu sichernden Quellen

        requiredActionIds - Die durchzuführenden Aktionen

        sinkProfileId - Die einzusetzende Senke

        timeExpression - Der Zeitpunkt, zu dem der Job durchgeführt werden soll (realtime, weekly, monthly)

        keyRing - Das Schlüsselbundpasswort des Benutzers
        """
        if not "source_profile_ids" in data:
            raise ValueError('key "source_profile_id" is missing in argument "data".')
        #if not "required_action_ids" in data:
        #    raise ValueError('key "required_action_ids" is missing in argument "data".')
        if not "sink_profile_ids" in data:
            raise ValueError('key "sink_profile_id" is missing in argument "data".')
        if not "time_expression" in data:
            raise ValueError('key "time_expression" is missing in argument "data".')
        if not "key_ring" in data:
            raise ValueError('key "key_ring" is missing in argument "data".')

        params = {
            'sourceProfiles': data['source_profile_ids'],
            'actions': data['actions'],
            'sinkProfileId': data['sink_profile_ids'],
            'timeExpression': data['time_expression'],
            'keyRing': data['key_ring'],
            'jobTitle': data['job_title'],
        }
        
        for item in data['source_options']:
            params_key = str(params['sourceProfiles']) + "." + item
            params[params_key] = "true"
        
        return self._post(data=params)
    
    def put(self, job_id, data):
        """
        sourceProfileIds - Die zu sichernden Quellen

        requiredActionIds - Die durchzuführenden Aktionen

        sinkProfileId - Die einzusetzende Senke

        timeExpression - Der Zeitpunkt, zu dem der Job durchgeführt werden soll (realtime, weekly, monthly)

        keyRing - Das Schlüsselbundpasswort des Benutzers
        """
        if not "source_profile_ids" in data:
            raise ValueError('key "source_profile_id" is missing in argument "data".')
        #if not "required_action_ids" in data:
        #    raise ValueError('key "required_action_ids" is missing in argument "data".')
        if not "sink_profile_ids" in data:
            raise ValueError('key "sink_profile_id" is missing in argument "data".')
        if not "time_expression" in data:
            raise ValueError('key "time_expression" is missing in argument "data".')
        if not "key_ring" in data:
            raise ValueError('key "key_ring" is missing in argument "data".')

        params = {
            'sourceProfiles': data['source_profile_ids'],
            'actions': data['actions'],
            'sinkProfileId': data['sink_profile_ids'],
            'timeExpression': data['time_expression'],
            'keyRing': data['key_ring'],
            'jobTitle': data['job_title'],
        }
        
        for item in data['source_options']:
            params_key = str(params['sourceProfiles']) + "." + item
            params[params_key] = "true"
        
        return self._put(path=job_id + "/", data=params)
    
    def delete(self, job_id):
        return self._delete(path=job_id)

    def get_all(self):
        response = self._get()

        if response and 'backupJobs' in response:
            return response['backupJobs']
        else:
            return response
    
    def get(self, job_id):
        return self._get(path=job_id + "/")
    
    def get_job_status(self, job_id):
        return self._get(path=job_id + "/status/")

    #def get_file_status(self, file_id):
    #    return self._get(path=file_id + "/details/")

    def get_user_profile_status(self):
        return self._get(path="/status/overview/")

    def validate(self, job_id):
        return self._get(path="validate/%s/" % job_id)


class RestMetadata(RestBase):

    def __init__(self, username, path="meta/"):
        if not username:
            raise ValueError('argument "username" is missing.')
        self.username = username

        super(RestMetadata, self).__init__()
        self.base_url = "%s%s%s/" % (self.base_url, path, self.username)

    def get(self, profile_id):
        return self._get(path=profile_id + "/")


class RestSearch(RestBase):
    
    def __init__(self, username, path='backups/'):
        self.username = username
        super(RestSearch, self).__init__()
        self.base_url = "%s%s%s/" % (self.base_url, path, self.username)
    
    def get(self, search_id, data=None):
        params = {}
        if data:
            if "type" in data:
                params['type'] = data['type']
            if "source" in data:
                params['source'] = data['source']
        
        return self._get(path="%d/query/" % int(search_id), data=params)
        
    def post(self, data):
        params = {
            'keyRing': data['key_ring'],
            'query': data['query']
        }
        return self._post(path="search/", data=params)


class RestFile(RestBase):
    
    def __init__(self, username, path="jobs/"):
        if not username:
            raise ValueError('argument "username" is missing.')
        self.username = username
        
        super(RestFile, self).__init__()
        self.base_url = "%s%s%s/" % (self.base_url, path, self.username)
    
    def get(self, file_id):
        return self._get(path=file_id + "/details/")

