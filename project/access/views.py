# -*- coding: utf-8 -*-

# django
#from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth.decorators import login_required

# project
from access.forms import UserCreationForm, UserEmailVerificationForm, UserSettingsForm
from remote_api.rest import RestEmailVerification



import urlparse

from django.conf import settings
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm#, PasswordResetForm, SetPasswordForm, PasswordChangeForm
#from django.contrib.auth.models import User
#from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site




@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            netloc = urlparse.urlparse(redirect_to)[1]

            # Use default setting if redirect_to is empty
            if not redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Heavier security check -- don't allow redirection to a different
            # host.
            elif netloc and netloc != request.get_host():
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)
    else:
        if 'validated_email' in request.session:
            form = authentication_form(request, initial={'username': request.session['validated_email']})
        else:
            form = authentication_form(request)
    request.session.set_test_cookie()

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)

def logout(request, next_page=None,
           template_name='registration/logged_out.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           current_app=None, extra_context=None):
    """
    Logs out the user and displays 'You are logged out' message.
    """
    auth_logout(request)
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if redirect_to:
        netloc = urlparse.urlparse(redirect_to)[1]
        # Security check -- don't allow redirection to a different host.
        if not (netloc and netloc != request.get_host()):
            return HttpResponseRedirect(redirect_to)

    if next_page is None:
        current_site = get_current_site(request)
        context = {
            'site': current_site,
            'site_name': current_site.name,
            'title': _('Logged out')
        }
        if extra_context is not None:
            context.update(extra_context)
        return TemplateResponse(request, template_name, context,
                                current_app=current_app)
    else:
        # Redirect to this page until the session has been cleared.
        return HttpResponseRedirect(next_page or request.path)



def signup(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        user = authenticate(username=user.username, password=request.POST['password1'])
        if user is not None:
            if user.is_active:
                print "#alsdkjfalsdjflkjasdflkjasdflkjasdf"
                django_login(request, user)
                request.session['key_ring'] = request.POST['password1']
        return redirect('verify-email')
    
    context = {
        'form': form,
    }
    return render_to_response(
        "www/access/signup.html",
        context,
        context_instance=RequestContext(request)
    )


def verify_email(request, verify_hash=None):
    if request.method == 'POST' or verify_hash:
        data = {
            "verify_hash": verify_hash,
        }
        form = UserEmailVerificationForm(request.POST or data)
        if form.is_valid():
            email = form.cleaned_data['email']
            messages.add_message(request, messages.INFO, _('user\'s email %s is verified' % email))
            request.session['validated_email'] = email
            return redirect('datasource-select')
        #else:
        #    messages.add_message(request, messages.INFO, 'user\'s email couldn\'t be verified')
    else:
        form = UserEmailVerificationForm()
    
    return render_to_response(
        "www/access/verify_email.html",
        {
            "form": form,
        },
        context_instance=RequestContext(request)
    )


@login_required
def verify_email_resend(request):
    rest = RestEmailVerification()
    result = rest.resend(username=request.user.username)
    if 'errorType' in result:
        messages.add_message(request, messages.ERROR, _(result['errorMessage']))
        return redirect('index')
    else:
        messages.add_message(request, messages.SUCCESS, _('New verification email has been sent.'))
        return redirect('verify-email')


@login_required
def user_settings(request):
    form = UserSettingsForm(request.user, request.POST or None)
    if form.is_valid():
        result = form.save()
        
        if result and 'errorMessage' in result:
            messages.add_message(request, messages.ERROR, _(result['errorMessage']))
        return redirect('user-settings')
    
    return render_to_response(
        'www/access/user_settings.html',
        {
            "form": form,
        },
        context_instance=RequestContext(request)
    )
