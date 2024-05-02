from abc import ABC, abstractmethod
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime
from django.conf import settings
from django.core.serializers import serialize
from django.forms import Form
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt 
from panel.forms import AddNewsletter, DeleteNewsletter, PublicateNewsletter, UpdateNewsletter, UpdateNewsletterViews, FileUploadForm, GetNewslettersId, UpdateNewsletterCategory, GetExel
from panel.models import MyModel
from typing import Callable
from .base import BaseAPI
from .utils import get_post, send_post, update_post_data
import json
import os

class BaseBotAPI(BaseAPI, ABC):

    @classmethod
    @csrf_exempt
    def router(cls, request) -> JsonResponse:
        obj = cls(request=request)
        if (error := obj.is_valid):
            return error
        result = obj.handle_request()
        obj.response_middleware(result)
        return result
    
    def handle_request(self) -> JsonResponse:
        if (result := self.run_job()):
            return self.OK(result=result)
        else:
            return self.BAD(err="server error")
        
    def run_job(self):
        try:
            return self.job()
        except Exception as e:
            print(f"Error in function 'BaseBotAPI.run_job': {e}")
        
    @abstractmethod
    def job(self):
        pass
    

class NewPost(BaseBotAPI):
    form_template: Form = AddNewsletter

    def job(self):
        MyModel.delete_old()
        return MyModel.add_or_update_record(**self.form.data)

class DeletePost(BaseBotAPI):
    form_template: Form = DeleteNewsletter

    def job(self):
        return MyModel.delete_record(**self.form.data)
    
class UpdatePostCategory(BaseBotAPI):
    form_template: Form = UpdateNewsletterCategory

    def job(self):
        return MyModel.update_category(**self.form.data)

class UpdatePost(BaseBotAPI):
    form_template: Form = UpdateNewsletter
    
    def job(self):
        return MyModel.update_text(**self.form.data)

class UpdatePostViews(BaseBotAPI):
    form_template: Form = UpdateNewsletterViews
    
    def job(self):
        return MyModel.update_views(**self.form.data)

class GetPostsId(BaseBotAPI):
    form_template: Form = GetNewslettersId
    
    def job(self):
        data = MyModel.get_posts_id(**self.form.data)
        data = data[:settings.VIEWS_HISTORY_LIMIT]
        return list(data.values())

class SendPost(BaseBotAPI):
    form_template: Form = PublicateNewsletter

    def job(self) -> JsonResponse:
        newsletter = get_post(self.form.data["id"], False)
        payload = {
            "text" : newsletter.text,
            "data" : newsletter.data,
            "photo" : newsletter.photo,
            "project" : self.form.data["project"],
            "time" : self.form.data.get(
                "datetime",
                datetime.now().strftime('%Y-%m-%dT%H:%M')
            ),
        }

        data = {
            "type": "send_post",
            "send_post": payload
        }
        async_to_sync(get_channel_layer().group_send)("websocket", data)

        return send_post(payload)

class UploadMedia(BaseAPI):
    form_template: Form = FileUploadForm
    remaining_links: list = list()

    def save_files(self):
        media_files = self.request.FILES.getlist('files[]')
        for file in media_files:
            file_name = str(file)
            file_path = os.path.join(settings.MEDIA_FOLDER, file_name)
            file_url = f"{settings.SERVER_URI}{settings.MEDIA_URL}{file_name}"
            with open(file_path, 'wb') as media_file:
                for chunk in file.chunks():
                    media_file.write(chunk)
            self.remaining_links.append(file_url)

    def validate_form(self) -> bool:
        self.form = self.form_template(self.request.POST)
        self.remaining_links = json.loads(
            self.form.data['remainingLinks']
        )
        return self.form.is_valid()

    def handle_request(self) -> JsonResponse:
        self.save_files()
        if update_post_data(self.form.data['post_id'], self.remaining_links):
            return self.OK()
        else:
            return self.BAD()
        