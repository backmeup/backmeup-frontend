# -*- coding: utf-8 -*-

from access.models import User

from remote_api.rest import RestUser

class RestBackend(object):
    """foo"""
    
    supports_inactive_user = False
    
    def authenticate(self, username=None, password=None):
        """foo"""
        
        remote_user = RestUser(username)
        login_result = remote_user.check_login({'password':password})
        if not 'errorMessage' in login_result:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # user will have an empty password
                user = User.objects.create_user(username, '')
                user.save()
            return user
        return None

    def get_user(self, user_id):
        """Retrieve the user's entry in the User model if it exists"""

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
