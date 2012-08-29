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
        response = requests.delete(self.base_url + path, data=data)
        if settings.DEBUG:
            print "#######################_delete url:", self.base_url + path
            print "#######################_delete data:", data
            print "#######################_delete", response
            print "#######################_delete", response.json
        return response
    
    def _get(self, path="", data=None):
        response = requests.get(self.base_url + path, data=data)
        if settings.DEBUG:
            print "##########################_get url:", self.base_url + path
            print "##########################_get data:", data
            print "##########################_get", response
            print "##########################_get", response.json
        if response.status_code == 404 or response.status_code == 401:
            return False
        elif response.status_code == 204:
            return True
        else:
            return response.json
    
    def _post(self, path="", data=None):
        response = requests.post(self.base_url + path, data=data)
        if settings.DEBUG:
            print "#########################_post url:", self.base_url + path
            print "#########################_post data:", data
            print "#########################_post", response
            print "#########################_post", response.json
        if response.status_code == 204:
            return True
        elif response.status_code == 400 or response.status_code == 404 or response.status_code == 401:
            return False
        return response.json
    
    def _put(self, path="", data=None):
        response = requests.put(self.base_url + path, data=data)
        if settings.DEBUG:
            print "##########################_put url:", self.base_url + path
            print "##########################_put data:", data
            print "##########################_put", response
            print "##########################_put", response.json
        return response


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
        req_params['old_password'] = data['old_password']
        
        if data['password']:
            req_params['password'] = data['password']
        if data['keyRing']:
            req_params['keyRing'] = data['keyRing']
        if data['email']:
            req_params['email'] = data['email']
        
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


class RestDatasource(RestBase):
    def __init__(self, path="datasources/"):
        super(RestDatasource, self).__init__()
        self.base_url = self.base_url + path
    
    def get_all(self):
        return self._get()['sources']
    
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
    
    def get_all(self):
        return self._get(path="profiles/")['sourceProfiles']
    
    def delete(self, profile_id):
        if not profile_id:
            raise ValueError('argument "profile_id" is missing.')
        return self._delete(path="profiles/" + profile_id)
    
    def options(self, profile_id):
        if not profile_id:
            raise ValueError('argument "profile_id" is missing.')
        
        return self._get(path="profiles/" + profile_id + "/options")
        
    def put(self, profile_id, source_options):
        if not profile_id:
            raise ValueError('argument "profile_id" is missing.')
        if not source_options:
            raise ValueError('argument "source_options" is missing.')
        
        data = {
            "sourceOptions": source_options,
        }
        return self._put(path="profiles/" + profile_id, data=data)
    
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
        return self._get()['sinks']
    
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
    
    def get_all(self):
        return self._get(path="profiles/")['sinkProfiles']
    
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
        if not "profile_name" in data:
            raise ValueError('key "profile_name is missing in argument "data".')
        #if not "key_ring" in data:
        #    raise ValueError('key "key_ring is missing in argument "data".')
        params = {
            "keyRing": data["key_ring"],
            #"sourceOptions": json.dumps(data['source_options']),
        }
        return self._post(path="%s/auth/post" % profile_id, data=params)


class RestAction(RestBase):
    
    def __init__(self, path="actions/"):
        super(RestAction, self).__init__()
        self.base_url = self.base_url + path
    
    def get_all(self):
        return self._get()
    
    def options(self, action_id):
        return self._get(path=action_id + "/options/")
    
    def post(self, data):
        if not "name" in data:
            raise ValueError('key "name" is missing in argument "data".')
        if not "filename" in data:
            raise ValueError('key "filename" is missing in argument "data".')
        
        params = {
            'name': data['name'],
            'filename': data['filename'],
        }
        
        return self._post(data=data)
    
    def delete(self, action_id):
        return self._delete(path=action_id + "/")


class RestJobs(RestBase):
    
    def __init__(self, username, path="jobs/"):
        if not username:
            raise ValueError('argument "username" is missing.')
        self.username = username
        
        super(RestJobs, self).__init__()
        self.base_url = "%s%s%s/" % (self.base_url, path, self.username)
    
    def post(self):
        """
        sourceProfileIds - Die zu sichernden Quellen

        requiredActionIds - Die durchzuführenden Aktionen

        sinkProfileId - Die einzusetzende Senke

        timeExpression - Der Zeitpunkt, zu dem der Job durchgeführt werden soll (realtime, weekly, monthly)

        keyRing - Das Schlüsselbundpasswort des Benutzers
        """
        if not "source_profile_id" in data:
            raise ValueError('key "source_profile_id" is missing in argument "data".')
        if not "required_action_ids" in data:
            raise ValueError('key "required_action_ids" is missing in argument "data".')
        if not "sink_profile_id" in data:
            raise ValueError('key "sink_profile_id" is missing in argument "data".')
        if not "time_expression" in data:
            raise ValueError('key "time_expression" is missing in argument "data".')
        if not "key_ring" in data:
            raise ValueError('key "key_ring" is missing in argument "data".')
        
        params = {
            'sourceProfileIds': data['source_profile_ids'],
            'requiredActionIds': data['required_action_ids'],
            'sinkProfileId': data['sink_profile_ids'],
            'timeExpression': data['time_expression'],
            'keyRing': data['key_ring'],
        }
        
        return self._post(data=data)
    
    def delete(self, job_id):
        return self._delete(path=job_id + "/status/")
    
    def get_user_status(self):
        return self._get()
    
    def get_job_status(self, job_id):
        return self._get(path=job_id + "/status/")
    
    def get_file_status(self, file_id):
        return self._get(path=file_id + "/details/")
    
    def get_user_profile_status(self):
        return self._get(path="/status/overview/")
    
    def validate(self, job_id):
        return self._get(path="validate/%s/" % job_id)
    
#
#class RestSearch(RestBase):
#    
#    def __init__(self, username, path="backups/"):
#        if not username:
#            raise ValueError('argument "username" is missing.')
#        self.username = username
#        
#        super(RestJobs, self).__init__()
#        self.base_url = "%s%s%s/" % (self.base_url, path, self.username)
#


class RestMetadata(RestBase):

    def __init__(self, username, path="meta/"):
        if not username:
            raise ValueError('argument "username" is missing.')
        self.username = username
        
        super(RestMetadata, self).__init__()
        self.base_url = "%s%s%s/" % (self.base_url, path, self.username)
    
    def get(self, profile_id):
        return self._get(path=profile_id + "/")
    
    