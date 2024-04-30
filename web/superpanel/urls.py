# -*- coding: utf-8 -*-

from django.urls import path

from . import views

app_name = 'superpanel'

urlpatterns = [
     path('dashboard/', views.index_view, name='dashboard'),
     path('users/', views.users_list, name='users'),
     path('user/', views.user_info, name='user'),
     path('edit_user/', views.edit_user, name='edit_user'),
     

]
