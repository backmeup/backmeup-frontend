# -*- coding: utf-8 -*-

# django
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

# project
from access.models import User
from remote_api.rest import RestUser, RestEmailVerification


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and password.
    """
    # this will be username AND email becaus the email field is required
    email = forms.EmailField(label=_('Email'), max_length=254)

    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput, 
        help_text=_("Your password needs to be at least %s characters long." % settings.ACCESS_MIN_PASSWORD_LENGTH))
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))

    #key_ring1 = forms.CharField(label=_("KeyRing Password"), widget=forms.PasswordInput)
    #key_ring2 = forms.CharField(label=_("KeyRing Password confirmation"), widget=forms.PasswordInput,
    #    help_text=_("Enter the same KeyRing Password as above, for verification."))

    class Meta:
        model = User
        fields = ("email",)

    #def clean_username(self):
    #    return self.cleaned_data["username"]
    
    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            # check if remote api knows user
            remote_user = RestUser(email)
            result = remote_user.get()
        
            if 'errorType' in result and result['errorType'] == 'org.backmeup.model.exceptions.UnknownUserException':
                # remote api doesn't know user, thus check with local db
                old_user = User.objects.get(username=email)
                # seems like the user exists (no exception) in "our" db, but not
                # according to the rest api. thus the user is deleted.
                old_user.delete()
                return email
        except User.DoesNotExist:
            return email
        
        raise forms.ValidationError(_("A user with that email already exists."))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        
        if len(password1) < settings.ACCESS_MIN_PASSWORD_LENGTH:
            raise forms.ValidationError(_("Password must be at least %d chars." % settings.ACCESS_MIN_PASSWORD_LENGTH))
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        
        return password2

    #def clean(self):
    #    if not self.errors:
    #        self.cleaned_data['username'] = self.cleaned_data['email']
    #    super(UserCreationForm, self).clean()
    #    return self.cleaned_data

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password("")
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        
        remote_user = RestUser(user.username)
        response = remote_user.post({
            'password': self.cleaned_data["password1"],
            'keyRing': self.cleaned_data['password1'],
            'email': self.cleaned_data['email'],
        })

        if response == False:
            raise Exception

        if commit:
            user.save()
        return user


class DebugUserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and password.
    """
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^[\w.@+-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
        error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
    email = forms.EmailField(label=_('Email'), max_length=254)

    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))

    key_ring1 = forms.CharField(label=_("KeyRing Password"), widget=forms.PasswordInput)
    key_ring2 = forms.CharField(label=_("KeyRing Password confirmation"), widget=forms.PasswordInput,
        help_text=_("Enter the same KeyRing Password as above, for verification."))

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            # check if remote api knows user
            remote_user = RestUser(username)
            result = remote_user.get()

            if 'errorType' in result and result['errorType'] == 'org.backmeup.model.exceptions.UnknownUserException':
                # remote api doesn't know user, thus check with local db
                User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise forms.ValidationError(_("A user with that username already exists."))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def clean_key_ring2(self):
        key_ring1 = self.cleaned_data.get("key_ring1", "")
        key_ring2 = self.cleaned_data["key_ring2"]
        if key_ring1 != key_ring2:
            raise forms.ValidationError(_("The two KeyRing Password fields didn't match."))
        return key_ring2

    def save(self, commit=True):
        user = super(DebugUserCreationForm, self).save(commit=False)
        #user.set_password(self.cleaned_data["password1"])
        user.set_password("")

        remote_user = RestUser(user.username)
        response = remote_user.post({
            'password': self.cleaned_data["password1"],
            'keyRing': self.cleaned_data['key_ring1'],
            'email': self.cleaned_data['email'],
        })

        if response == False:
            raise Exception

        if commit:
            user.save()
        return user


class UserEmailVerificationForm(forms.Form):

    verify_hash = forms.CharField(label=_("Verification Key"))

    def clean(self):
        rest_api = RestEmailVerification()

        result = rest_api.verify(self.cleaned_data["verify_hash"])
        if "errorMessage" in result:
            raise forms.ValidationError(_(result['errorMessage']))
        else:
            return {
                'email': result['username'],
            }


class UserSettingsForm(forms.Form):

    email = forms.EmailField(label=_('Email'), max_length=254, required=False)

    new_password1 = forms.CharField(label=_("New Password"), widget=forms.PasswordInput, required=False)
    new_password2 = forms.CharField(label=_("New Password confirmation"), widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."), required=False)

    #new_key_ring1 = forms.CharField(label=_("New KeyRing Password"), widget=forms.PasswordInput, required=False)
    #new_key_ring2 = forms.CharField(label=_("New KeyRing Password confirmation"), widget=forms.PasswordInput,
    #    help_text=_("Enter the same KeyRing Password as above, for verification."), required=False)
    
    old_password = forms.CharField(label=_("Current Password"), widget=forms.PasswordInput,
        help_text=_("Enter your current password for verification."))
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        kwargs['initial'] = {
            'email': self.user.username,
        }
        super(UserSettingsForm, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        remote_user = RestUser(self.user.username)
        if not remote_user.check_login(old_password):
            raise forms.ValidationError(_("Your old password was entered incorrectly. Please enter it again."))
        return old_password

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get("new_password1", "")
        new_password2 = self.cleaned_data["new_password2"]
        if new_password1 == "" and new_password2 == "":
            return new_password2
        if new_password1 != new_password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return new_password2
    
    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            # check if remote api knows user
            remote_user = RestUser(email)
            result = remote_user.get()
        
            if 'errorType' in result and result['errorType'] == 'org.backmeup.model.exceptions.UnknownUserException':
                # remote api doesn't know user, thus check with local db
                old_user = User.objects.get(username=email)
                # seems like the user exists (no exception) in "our" db, but not
                # according to the rest api. thus the user is deleted.
                old_user.delete()
                return email
        except User.DoesNotExist:
            return email
        
        raise forms.ValidationError(_("A user with that email already exists."))
    
    def save(self):
        rest_api = RestUser(self.user.username)
        data = {}
        
        old_password = self.cleaned_data['old_password']
        new_password = self.cleaned_data.get('new_password1', False)
        new_key_ring = self.cleaned_data.get('new_password1', False)
        new_email = self.cleaned_data.get('email', self.user.username)
        
        data['old_password'] = old_password
        if new_password:
            data['password'] = new_password
        if new_key_ring:
            data['keyRing'] = new_key_ring
        if not new_email == self.user.username:
            data['email'] = new_email
            data['username'] = new_email
        
        result_rest = rest_api.put(data)
        
        if result_rest == True and not new_email == self.user.username:
            self.user.username = new_email
            self.user.email = new_email
            self.user.save()
        
        return result_rest


class DebugUserSettingsForm(forms.Form):
    email = forms.EmailField(label=_('Email'), max_length=254, required=False)

    new_password1 = forms.CharField(label=_("New Password"), widget=forms.PasswordInput, required=False)
    new_password2 = forms.CharField(label=_("New Password confirmation"), widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."), required=False)

    new_key_ring1 = forms.CharField(label=_("New KeyRing Password"), widget=forms.PasswordInput, required=False)
    new_key_ring2 = forms.CharField(label=_("New KeyRing Password confirmation"), widget=forms.PasswordInput,
        help_text=_("Enter the same KeyRing Password as above, for verification."), required=False)
    
    old_password = forms.CharField(label=_("Current Password"), widget=forms.PasswordInput,
        help_text=_("Enter your current password for verification."))
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        kwargs['initial'] = {
            'email': self.user.username,
        }
        super(UserSettingsForm, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        remote_user = RestUser(self.user.username)
        if not remote_user.check_login(old_password):
            raise forms.ValidationError(_("Your old password was entered incorrectly. Please enter it again."))
        return old_password

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get("new_password1", "")
        new_password2 = self.cleaned_data["new_password2"]
        if new_password1 == "" and new_password2 == "":
            return new_password2
        if new_password1 != new_password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return new_password2

    def clean_new_key_ring2(self):
        new_key_ring1 = self.cleaned_data.get("new_key_ring1", "")
        new_key_ring2 = self.cleaned_data["new_key_ring2"]
        if new_key_ring1 == "" and new_key_ring2 == "":
            return new_key_ring2
        if new_key_ring1 != new_key_ring2:
            raise forms.ValidationError(_("The two KeyRing Password fields didn't match."))
        return new_key_ring2

    def save(self):
        rest_api = RestUser(self.user.username)
        data = {}
        
        old_password = self.cleaned_data['old_password']
        new_password = self.cleaned_data.get('new_password1', False)
        new_key_ring = self.cleaned_data.get('new_key_ring1', False)
        new_email = self.cleaned_data.get('email', self.user.username)
        
        data['old_password'] = old_password
        if new_password:
            data['password'] = new_password
        if new_key_ring:
            data['keyRing'] = new_key_ring
        if not new_email == self.user.username:
            data['email'] = new_email

        return rest_api.put(data)

