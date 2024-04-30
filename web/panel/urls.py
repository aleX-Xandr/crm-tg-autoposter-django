# -*- coding: utf-8 -*-

from django.urls import path
from . import views
from .routers import *





app_name = 'panel'

urlpatterns = [
     path('dashboard/', Dashboard.router, name='dashboard'),

     path('channels/', ChannelsList.router, name='channels'),
     path('sites/', SitesList.router, name='sites'),
     path('news/', NewsList.router, name='news'),

     path('get_news/', NewsListAPI.router, name='get_news'),

     path('channel/', ChannelInfo.router, name='channel'),
     path('edit_channel/', EditChannel.router, name='edit_channel'),
     path('post/', SendPost.router, name='post'),
     path('newsletter/', NewsInfo.router, name='newsletter'),

     path('add_post/', NewPost.router, name='add_post'),
     path('update_post/', UpdatePost.router, name='update_post'),
     path('update_post_views/', UpdatePostViews.router, name='update_post_views'),
     path('delete_post/', DeletePost.router, name='delete_post'),
     path('update_post_category/', UpdatePostCategory.router, name='update_post_category'),
     path('get_last_msgs_id/', GetPostsId.router, name='get_last_msgs_id'),
     
     
     path('upload/', UploadMedia.router, name='upload_files'),
     path('add_data/', views.add_data, name='add_data'),
     path('delete_data/', views.delete_data, name='delete_data'),

     path('get_exel/', GetExelDocument.router, name='get_exel')


]
