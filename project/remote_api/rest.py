# -*- coding: utf-8 -*-

import requests

REST_API_BASE_URL = "http://localhost:8080/"

# TODO 
# move all requests api specific code to RestBase

class RestBase(object):
    
    def __init__(self, url=REST_API_BASE_URL):
        self.base_url = url
    
    def _delete(self, path="", data=None):
        req = requests.delete(self.base_url + path, data=data)
        return req
    
    def _get(self, path="", data=None):
        req = requests.get(self.base_url + path, data=data)
        return req
    
    def _post(self, path="", data=None):
        req = requests.post(self.base_url + path, data=data)
        return req
    
    def _put(self, path="", data=None):
        req = requests.put(self.base_url + path, data=data)
        return req


class RestUser(RestBase):
    
    def __init__(self, username=None, path="users/"):
        if not username:
            raise ValueError('argument "username" is missing.')
        self.username = username
        
        super(RestUser, self).__init__()
        self.base_url = "%s%s%s/" % (self.base_url, path, self.username)
    
    def delete(self):
        return self._delete()
    
    def get(self):
        response = self._get()
        if response.status_code == 404:
            return False
        else:
            return response.json
        
    def post(self, data):
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
    
    def login_sic(self, password):
        if not username:
            raise ValueError('argument "username" is missing.')
        if not password:
            raise ValueError('argument "password" is missing.')
        
        req_params = {
            'password': password,
        }
        
        response = self._get('/login', req_params)
        if response.status_code == 204:
            return True
        else:
            return False

