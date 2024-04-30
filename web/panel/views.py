# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import JsonResponse
from django.core.cache import cache
cache.clear()
from . import utils
from accounts.models import UserDatabase
from django.contrib.auth.decorators import login_required


methods_add = {"channel": utils.add_channel, "site": utils.add_site}
methods_delete = {"channel": utils.delete_channel, "site": utils.delete_site}

def change_data(request, methods):
    if request.method != "POST":
        return JsonResponse({"status": "bad request"}, status=400)
    method_type = request.POST.get('type')
    method_data = request.POST.get('data')
    method_flags = request.POST.get('flags')
    user = UserDatabase.get_record_by_login(request.COOKIES.get('username'))
    if not user is None and user.rights != "":
        rights = request.COOKIES.get('access')
        if rights is None:
            rights = user.rights.split(",")[0]
        if not rights or rights not in user.rights.split(","):
            return redirect('panel:dashboard')
        res = methods[method_type](method_data, rights, method_flags)
        if res:
            return JsonResponse({"status": "success"}, status=200)
        else:
            return JsonResponse({"status": "error while changing data"}, status=500)
        
@login_required
def add_data(request):
    return change_data(request, methods_add)

@login_required
def delete_data(request):
    return change_data(request, methods_delete)
    