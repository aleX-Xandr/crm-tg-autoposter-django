# -*- coding: utf-8 -*-

from django.shortcuts import redirect, render
from django.http import JsonResponse 
from django.views.decorators.csrf import csrf_exempt 
from .forms import FileUploadForm  
import json, os
from django.core.cache import cache
cache.clear()
from . import utils
from accounts.models import UserDatabase

def index_view(request):
    if request.user.is_authenticated:
        if request.user.username != "superadmin":
            return redirect("panel:dashboard")
        return render(
            request=request,
            template_name='superadminpanel/index.html',
        )
    return redirect('accounts:login')

def users_list(request):
    if request.user.is_authenticated:
        if request.user.username != "superadmin":
            return redirect("panel:dashboard")
        context = {"users": UserDatabase.get_sorted_records()}
        return render(request, 'superadminpanel/users.html', context)
    return redirect('accounts:login')

def user_info(request):
    if request.method == "GET" and request.user.is_authenticated:
        if request.user.username != "superadmin":
            return redirect("panel:dashboard")
        user = UserDatabase.get_record_by_login(request.GET.get('id', None), "id")
        # user.password = "*"*len(user.password)
        print(open("web/superpanel/projects.json").read())
        projects = json.loads(open("web/superpanel/projects.json").read())
        context = {"user": user, "projects": projects}
        return render(request, 'superadminpanel/user.html', context)
    return redirect('accounts:login')

def edit_user(request):
    if request.method == "POST" and request.user.is_authenticated:
        if request.user.username != "superadmin":
            return redirect("panel:dashboard")
        if UserDatabase.update_user(request.POST.get('id'), request.POST.get('access'), request.POST.get('text')):
            return JsonResponse({"status": "success"}, status=200)
        else:
            return JsonResponse({"status": "error while updating data"}, status=500)
    return JsonResponse({"status": "bad request"}, status=400)

def delete_user(request):
    if request.method == "POST" and request.user.is_authenticated:
        if request.user.username != "superadmin":
            return redirect("panel:dashboard")
        payload = {
            "id"           : request.POST.get('id'),
        }

        if UserDatabase.delete_user(payload=payload):
            return JsonResponse({"status": "success"}, status=200)
        else:
            return JsonResponse({"status": "error while updating data"}, status=500)
        

    return JsonResponse({"status": "bad request"}, status=400)

