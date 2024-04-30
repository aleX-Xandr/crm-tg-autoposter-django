# -*- coding: utf-8 -*-

from django.shortcuts import redirect


# Create your views here.
def redirect_route(request):
    if request.user.is_authenticated:
        redirect('panel:dashboard')
    return redirect('accounts:login')
