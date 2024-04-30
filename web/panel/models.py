from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import MultipleObjectsReturned
from datetime import datetime

class parser_site(models.Model):
    id = models.BigAutoField(primary_key=True)
    url = models.TextField()
    project = models.TextField()
    type = models.TextField()
    use_proxy = models.BooleanField(default = False)

    @classmethod    
    def create_record(cls, url:str, project:str, type:str, use_proxy:bool=False):
        if not cls.objects.filter(url=url,project=project).exists():
            return cls.objects.create(url=url, project=project, type=type, use_proxy=use_proxy)
        else:
            return False


    @classmethod    
    def delete_record(cls, url:str, project:str):
        try:
            record = cls.objects.get(url=url, project=project)
            record.delete()
            return True
        except Exception as E:
            print(E)

    @classmethod    
    def get_all_records(cls, project):
        try:
            all_records = cls.objects.filter(project=project)
            return all_records
        except Exception as e:
            print(f"An error occurred while retrieving records: {e}")
            return None


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    
class MyModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    chat_id = models.TextField(default='')
    text = models.TextField()
    source = models.TextField()
    time_stringify = models.TextField(default='')
    photo = models.TextField(default='')
    data = models.TextField(default='')
    time = models.DateTimeField(default=timezone.now)
    channel = models.TextField(default='')
    account = models.TextField(default='')
    views = models.IntegerField(default=0)
    category = models.TextField(default='channel_post')

    @classmethod
    def update_record(cls, data: dict, **kwargs) -> bool:
        try:
            record = cls.objects.get(**kwargs)
            for key, value in data.items():
                setattr(record, key, value)
            record.save()
            return True
        except cls.DoesNotExist:
            return False
            
    @classmethod
    def update_text(cls, text: str, **kwargs) -> bool:
        return cls.update_record(**kwargs, data={"text": text})
    
    @classmethod
    def update_views(cls, views: int, **kwargs) -> bool:
        return cls.update_record(**kwargs, data={"views": views})
    
    @classmethod
    def update_data(cls, data, **kwargs) -> bool:
        return cls.update_record(**kwargs, data={"data": data})

    @classmethod
    def update_category(cls, category: str, **kwargs) -> bool:
        return cls.update_record(**kwargs, data={"category": category})
    
    @classmethod    
    def delete_record(cls, id) -> bool:
        try:
            record = cls.objects.get(id=id)
            record.delete()
            return True
        except cls.DoesNotExist:
            return False

    @classmethod
    def delete_old(cls):
        try:
            one_month_ago = timezone.now() - timezone.timedelta(days=30)
            old_records = cls.objects.filter(time__lt=one_month_ago)
            old_records.delete()
        except Exception as e:
            print("delete_old Eroor: ", e)

    @classmethod
    def delete_old_2(cls):

        try:
            from django.utils import timezone

            # Вычислите время, которое находится на 12 часов назад от текущего времени
            twelve_hours_ago = timezone.now() - timezone.timedelta(hours=17)

            # Вызовите метод `filter` для вашей модели, чтобы выбрать записи, созданные после twelve_hours_ago
            old_o =cls.objects.filter(time__gte=twelve_hours_ago)
            print("OLD O: ", old_o)
            old_o.delete()
        except Exception as e:
            print("delete_old Eroor: ", e)


    # @classmethod
    # def replace_photo_url(cls, old_value="http://127.0.0.1:8000", new_value="http://134.209.195.23:8000"):
    #     cls.objects.filter(photo__icontains=old_value).update(photo=models.Func(models.F('photo'), models.Value(old_value), models.Value(new_value), function='REPLACE'))

    @classmethod
    def add_or_update_record(cls, chat_id, time_stringify, text, source, photo, channel, account, views=0, data="None", category="channel_post"):
        time_threshold = timezone.now() - timezone.timedelta(seconds=30)
        record_id = None
        try:
            if data == "None" and text != "":
                existing_record = cls.objects.get(source=source, text=text, channel=channel, account=account)
                record_id = existing_record.id
            else:
                existing_record = cls.objects.get(source=source, time__gt=time_threshold, channel=channel, account=account)
                if text != '' and existing_record.text != '':
                    new_record = cls(chat_id=chat_id, source=source, time=timezone.now(), time_stringify=time_stringify, data=data, text=text, photo=photo, channel=channel, account=account, views=views, category=category)
                    new_record.save()
                    record_id = new_record.id
                else:
                    existing_record.data += "|||" + data
                    existing_record.text += text
                    if photo != "None":
                        existing_record.photo = photo
                    record_id = existing_record.id
                    existing_record.save()
        except cls.DoesNotExist:
            new_record = cls(chat_id=chat_id, source=source, time=timezone.now(), time_stringify=time_stringify, data=data, text=text, photo=photo, channel=channel, account=account, views=views, category=category)
            new_record.save()
            record_id = new_record.id
        except MultipleObjectsReturned:
            existing_record = cls.objects.filter(source=source, time__gt=time_threshold).first()
            if text != '' and existing_record.text != '':
                new_record = cls(chat_id=chat_id, source=source, time=timezone.now(), time_stringify=time_stringify, data=data, text=text, photo=photo, channel=channel, account=account, views=views, category=category)
                new_record.save()
                record_id = new_record.id
            else:
                existing_record.data += "|||" + data
                existing_record.text += text
                if photo != "None":
                    existing_record.photo = photo
                existing_record.save()
                record_id = existing_record.id
        except Exception as e:
            print(f"ERROR WHILE SAVING POST TO DB: {e}")
        finally:
            return record_id
        
    @classmethod
    def get_posts_id(cls, partial_chat_id):
        try:
            return cls.objects.filter(chat_id__icontains=partial_chat_id).values('chat_id', 'views').order_by('-time')
        except Exception as e:
            print(f"Error in function 'MyModel.get_posts_id': {e}")
            return []

    @classmethod
    def get_sorted_records(cls, categories_string=None, account="first", sorting_by_views="", keyword="", time_range=["", ""], source=""):
        if not categories_string:
            result = cls.objects.filter(account__contains=account)
        else:
            channels = categories_string.split("; ")
            result = cls.objects.filter(channel__in=channels, account__contains=account)
        if time_range[0] and time_range[1]:
            result = result.filter(time__range=time_range) #["2011-01-01", "2011-01-31"]
        if keyword:
            result = result.filter(text__icontains=keyword) #["2011-01-01", "2011-01-31"]
        if source == "onlyTg":
            result = result.filter(chat_id__icontains="https://t.me/")
        elif source == "onlyWeb":
            result = result.exclude(chat_id__icontains="https://t.me/")
        if sorting_by_views == "true":
            return result.order_by('-views')
        else:
            return result.order_by('-time')
        
    @classmethod
    def get_categories(cls, account="first"):
        return cls.objects.filter(account__contains=account).values('channel').distinct()
        
    @classmethod
    def get_record_by_id(cls, record_id):
        try:
            return cls.objects.get(id=record_id)
        except cls.DoesNotExist:
            return False

    @classmethod
    def get_record_from_xlsx(cls, 
                             start_time:datetime,
                             finish_time:datetime, 
                             phrase:str,
                             sites:list[str]):
        query = cls.objects.all() 
        if start_time and finish_time:
            query = query.filter(
                time__gte=start_time,
                time__lte=finish_time,
            )
        if phrase:
            query = query.filter(text__icontains=phrase)
        if sites:
            query = query.filter(channel__in=sites)
        return query
# MyModel.replace_photo_url()