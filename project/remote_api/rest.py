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
            print "...  ..."
            print "### [DELETE]", self.base_url + path
            print "request params:", json.dumps(data, indent=2)
            print "### response.status:", response.status_code
            print "### response.json:", json.dumps(response.json, indent=2)
            print "............................."
        return response

    def _get(self, path="", data=None):
        response = requests.get(self.base_url + path, data=data)
        
        if settings.DEBUG:
            print "### [GET]", self.base_url + path
            print "request params:", json.dumps(data, indent=2)
            print "### response.status:", response.status_code
            print "### response.json:", json.dumps(response.json, indent=2)
            print "............................."
        if response.status_code == 204:
            return True
        return response.json

    def _post(self, path="", data=None):
        response = requests.post(self.base_url + path, data=data)
        
        if settings.DEBUG:
            print "### [POST]", self.base_url + path
            print "request params:", json.dumps(data, indent=2)
            print "### response.status:", response.status_code
            print "### response.json:", json.dumps(response.json, indent=2)
            print "............................."
        if response.status_code == 204:
            return True
        return response.json

    def _put(self, path="", data=None):
        response = requests.put(self.base_url + path, data=data)

        if settings.DEBUG:
            print "### [PUT]", self.base_url + path
            print "request params:", json.dumps(data, indent=2)
            print "### response.status:", response.status_code
            print "### response.json:", json.dumps(response.json, indent=2)
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
        
        data
         * password
         * keyRing
         * email
        
        '''
        return self._post('register', data)

    def put(self, data):
        '''
        change user data
        
        data
         * password
         * keyRing
         * email
         * username
        
        '''
        return self._put(data=data)

    def check_login(self, data):
        '''
        checks if user-password combination is valid to login.

        the actual login and session handling is done by the backmeup-frontend.
        
        data
         * password
        '''
        return self._post(path='login/', data=data)


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
        return self._delete(path="profiles/" + profile_id)

    def options(self, profile_id, data):
        u'''
        path
         * profile_id
        data
         * keyRing
        '''
        profile_id = str(profile_id)
        return self._post(path="profiles/" + profile_id + "/options", data=data)

    def put(self, profile_id, job_id, source_options):
        '''
        data
         * sourceOptions
        '''
        return self._put(path="profiles/" + profile_id + "/" + str(job_id), data=data)

    def auth(self, datasource_id, data):
        '''
        data
         * profileName
         * keyRing
        '''
        return self._post(path="%s/auth" % datasource_id, data=data)

    def auth_post(self, profile_id, data):
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
        u'''
        data
         * profileName
         * keyRing
        '''
        return self._post(path="%s/auth" % datasink_id, data=data)

    def auth_post(self, profile_id, data):
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
        '''
        data
         * name
         * filename
        '''
        return self._post(data=data)

    def delete(self, action_id):
        return self._delete(path=action_id + "/")


class RestJobs(RestBase):

    def __init__(self, username, path="jobs/"):
        self.username = username
        super(RestJobs, self).__init__()
        self.base_url = "%s%s%s/" % (self.base_url, path, self.username)

    def post(self, data):
        """
        data
         * sourceProfiles
         * actions
         * sinkProfileId
         * timeExpression
         * keyRing
         * jobTitle
        """
        return self._post(data=data)
    
    def put(self, job_id, data):
        """
        data:
         * sourceProfiles
         * actions
         * sinkProfileId
         * timeExpression
         * keyRing
         * jobTitle
        """
        return self._put(path=job_id + "/", data=data)
    
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

    def get_user_profile_status(self):
        return self._get(path="/status/overview/")

    def validate(self, job_id):
        return self._get(path="validate/%s/" % job_id)


class RestMetadata(RestBase):

    def __init__(self, username, path="meta/"):
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
        u'''
        data
         * type
         * source
        '''
        return self._get(path="%d/query/" % int(search_id), data=data)
        
    def post(self, data):
        u'''
        data
         * keyRing
         * query
        '''
        return self._post(path="search/", data=data)


class RestFile(RestBase):
    
    def __init__(self, username, path="jobs/"):
        self.username = username
        super(RestFile, self).__init__()
        self.base_url = "%s%s%s/" % (self.base_url, path, self.username)
    
    def get(self, file_id):
        return self._get(path=file_id + "/details/")

