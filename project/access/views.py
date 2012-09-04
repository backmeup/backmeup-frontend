# -*- coding: utf-8 -*-

# django
#from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

# project
from access.forms import UserCreationForm, UserEmailVerificationForm
from remote_api.rest import RestEmailVerification


def signup(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
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
        if form.is_valid() and form.save():
            messages.add_message(request, messages.INFO, 'user\'s email is verified')
            return redirect('select-datasource')
        else:
            messages.add_message(request, messages.INFO, 'user\'s email couldn\'t be verified')
    else:
        form = UserEmailVerificationForm()
    
    return render_to_response(
        "www/access/verify_email.html",
        {
            "form": form,
        },
        context_instance=RequestContext(request)
    )
