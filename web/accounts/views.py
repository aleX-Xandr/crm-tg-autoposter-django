# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.http import HttpResponse
from .forms import SignupForm
from .models import UserDatabase, change_user_password_by_login, delete_user_by_login
from datetime import datetime, timedelta
from django.http import JsonResponse 
import urllib


def sign_up_view(request):
    form_errors = ['']

    if request.method == 'POST':
        form = SignupForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            UserDatabase.add_or_update_record(request.POST.get('username'), request.POST.get('password1'))
            response = redirect('accounts:login')
            response.set_cookie('username', request.POST.get('username'), expires=datetime.now()+timedelta(days=30))
            response.set_cookie('password', request.POST.get('password1'), expires=datetime.now()+timedelta(days=30))
            return response
        else:
            form_errors = form.get_fields_errors(request)
    
    if form_errors[0] != '':
        error = form_errors
    else:
        error = ''
        
    form = SignupForm()
    return render(
        request=request, 
        template_name='registration/sign_up.html',
        context={
            'form': form,
            'username': request.POST.get('username') or '',
            'password1': request.POST.get('password1') or '',
            'password2': request.POST.get('password2') or '', 
            'error': error,
        },
    )


def login_view(request):
    form = None
    print("login_view")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            print("USERNAME: ", username)
            user = authenticate(username=username, password=password)

            UserDatabase.add_or_update_record(username, password)

            if user is not None:
                login(request, user)
                UserDatabase.add_or_update_record(username, password)
                messages.info(request, f"You are now logged in as {username}.")
                response = redirect('superpanel:users' if username == "superadmin" else 'panel:dashboard')
                try:
                    user = UserDatabase.get_record_by_login(request.POST.get('username'))
                    response.set_cookie('category', urllib.parse.quote(user.favourites.encode('utf-8')), expires=datetime.now()+timedelta(days=30))
                except Exception as e:
                    print(e)
                response.set_cookie('username', username, expires=datetime.now()+timedelta(days=30))
                response.set_cookie('password', password, expires=datetime.now()+timedelta(days=30))
                return response
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    

    form = AuthenticationForm() if form is None else form
    return render(
        request=request,
        template_name="registration/login.html",
        context={
            'login_form': form,
        },
    )

def edit_user_view(request):
    if request.method == "POST" and request.user.is_authenticated:
        if request.user.username != "superadmin":
            return redirect("panel:dashboard")
        if change_user_password_by_login(request.POST.get('login'), request.POST.get('password')):
            UserDatabase.update_pass(request.POST.get('login'), request.POST.get('password'))
            return JsonResponse({"status": "success"}, status=200)
        else:
            return JsonResponse({"status": "error while updating data"}, status=500)
    return JsonResponse({"status": "bad request"}, status=400)

def delete_view(request):
    if request.method == "POST" and request.user.is_authenticated:
        if request.user.username != "superadmin":
            return redirect("panel:dashboard")
        if delete_user_by_login(request.POST.get('login'), request.POST.get('password')):
            UserDatabase.delete_user(request.POST.get('login'))
            return JsonResponse({"status": "success"}, status=200)
        else:
            return JsonResponse({"status": "error while updating data"}, status=500)

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.") 
    return redirect("accounts:login")
