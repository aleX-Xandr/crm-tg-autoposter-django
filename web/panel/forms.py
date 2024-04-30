from datetime import datetime
from django.forms import Form, CharField, DateTimeField, IntegerField, JSONField
# from .models import UploadedFile
from django.core.exceptions import ValidationError

class FileUploadForm(Form):
    remainingLinks = CharField(max_length=1000)
    post_id = CharField(max_length=100)

class ChannelData(Form):
    id = IntegerField()
    
class ChannelEditor(Form):
    id = IntegerField()
    flag = CharField(max_length=5)


class NewsCategory(Form):
    category = CharField(required=False)
    
class NewsData(Form):
    id = IntegerField()
    
class PublicateNewsletter(Form):
    id = IntegerField()
    datetime = DateTimeField(
        required=False, 
        initial=datetime.now().strftime('%Y-%m-%dT%H:%M')
    )
    project = CharField(max_length=32)

class AddNewsletter(Form):
    chat_id = CharField()
    time_stringify = CharField()
    text = CharField(required=False)
    source = CharField()
    data = CharField(required=False, initial="None")
    photo = CharField(required=False, initial="None")
    channel = CharField()
    account = CharField()
    views = IntegerField(required=False, initial=0)
    category = CharField(required=False, initial="channel_post")

class UpdateNewsletter(Form):
    id = IntegerField()
    text = CharField()
    
class UpdateNewsletterViews(Form):
    id = IntegerField(required=False)
    chat_id = CharField(required=False)
    views = CharField()

class DeleteNewsletter(Form):
    id = IntegerField()


class UpdateNewsletterCategory(Form):
    chat_id = CharField()
    category = CharField(required=False, initial="channel_post")

class GetNewslettersId(Form):
    partial_chat_id = CharField()
    
class GetExel(Form):
    dateFrom = DateTimeField(required=False,initial="0001-01-01T00:00")
    dateTo = DateTimeField(required=False, initial="0001-01-01T00:01")
    keyword = CharField(required=False, initial="")
    category = CharField(required=False, initial=[])
