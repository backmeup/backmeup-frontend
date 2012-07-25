# -*- coding: utf-8 -*-

#from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from access.forms import UserCreationForm

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

def verify_email(request):
    context = {}
    return render_to_response(
        "www/access/verify_email.html",
        context,
        context_instance=RequestContext(request)
    )