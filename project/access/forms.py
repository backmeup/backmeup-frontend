# -*- coding: utf-8 -*-

# django
from django import forms
from django.utils.translation import ugettext_lazy as _

# project
from access.models import User
from remote_api.rest import RestUser, RestEmailVerification


class UserCreationForm(forms.ModelForm):
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
            if not remote_user.get():
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
        user = super(UserCreationForm, self).save(commit=False)
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

    def save(self):
        rest_api = RestEmailVerification()

        if rest_api.verify(self.cleaned_data["verify_hash"]):
            return True
        else:
            return False
