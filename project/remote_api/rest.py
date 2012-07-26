# -*- coding: utf-8 -*-

import json
import requests

REST_API_BASE_URL = "http://localhost:8080/"

# TODO 
# move all requests api specific code to RestBase

class RestBase(object):
    u'''
    To abstract the requests api
    '''
    
    def __init__(self, url=REST_API_BASE_URL):
        self.base_url = url
    
    def _delete(self, path="", data=None):
        req = requests.delete(self.base_url + path, data=data)
        return req
    
    def _get(self, path="", data=None):
        response = requests.get(self.base_url + path, data=data)
        if response.status_code == 404:
            return False
        elif response.status_code == 204:
            return True
        else:
            return response.json
    
    def _post(self, path="", data=None):
        req = requests.post(self.base_url + path, data=data)
        return req
    
    def _put(self, path="", data=None):
        req = requests.put(self.base_url + path, data=data)
        return req


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
        if not username:
            raise ValueError('argument "username" is missing.')
        if not password:
            raise ValueError('argument "password" is missing.')
        
        req_params = {
            'password': password,
        }
        
        return = self._get('/login', req_params)
        

class RestDatasource(RestBase):
    def __init__(self, path="datasources/"):
        super(RestDatasource, self).__init__()
        self.base_url = self.base_url + path
    
    def get_all(self):
        return self._get()
    
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
        return self._get(path="profiles/")
    
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
        if not "profile_name" in data:
            raise ValueError('key "profile_name is missing in argument "data".')
        if not "key_ring" in data:
            raise ValueError('key "key_ring is missing in argument "data".')
        params = {
            "keyRing": data["key_ring"],
            "sourceOptions": json.dumps(data['source_options']),
        }
        return self._post(path="%s/auth/post" % profile_id, data=params)


class RestDatasink(RestBase):
    
    def __init__(self, path='datasinks/'):
        super(RestDatasink, self).__init__()
        self.base_url = self.base_url + path
    
    def get_all(self):
        return self._get()
    
    def post(self, data):
        return self._post(data)
    
    def delete(self, datasink_id):
        return self._delete(path=datasink_id)
    

class RestDataskinProfile(RestBase):
    
    def __init__(self, username, path="datasinks/"):
        if not username:
            raise ValueError('argument "username" is missing.')
        self.username = username
        
        super(RestDatasourceProfile, self).__init__()
        self.base_url = "%s%s%s/" % (self.base_url, path, self.username)
    
    def get_all(self):
        return self._get(path="profiles/")
    
    def delete(self, profile_id):
        return self._delete(path="profiles/" + profile_id)
    
    def auth(self, datasink_id, data):
        if not "profile_name" in data:
            raise ValueError('key "profile_name is missing in argument "data".')
        if not "key_ring" in data:
            raise ValueError('key "key_ring is missing in argument "data".')
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
    
        