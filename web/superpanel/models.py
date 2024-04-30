from django.db import models
from django.utils import timezone
from django.core.exceptions import MultipleObjectsReturned
from collections import defaultdict


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


    @classmethod
    def update_record(cls, row_id, text):
        try:
            record = cls.objects.get(id=row_id)
            record.text = text
            record.save()
            return True
        except cls.DoesNotExist:
            return False


    @classmethod
    def update_data(cls, row_id, data):
        try:
            record = cls.objects.get(id=row_id)
            record.data = data
            record.save()
            return True
        except cls.DoesNotExist:
            return False
            
    @classmethod    
    def delete_record(cls, row_id):
        try:
            record = cls.objects.get(id=row_id)
            record.delete()
            return True
        except cls.DoesNotExist:
            return False

    @classmethod
    def delete_old(cls):
        try:
            one_week_ago = timezone.now() - timezone.timedelta(days=7)
            old_records = cls.objects.filter(time__lt=one_week_ago)
            old_records.delete()
        except Exception as e:
            print("delete_old Eroor: ", e)

    @classmethod
    def add_or_update_record(cls, chat_id, time_stringify, text, source, data, photo, channel, account):
        time_threshold = timezone.now() - timezone.timedelta(seconds=5)
        record_id = None
        try:
            if data == "None" and text != "":
                existing_record = cls.objects.get(source=source, text=text, channel=channel, account=account)
                record_id = existing_record.id
            else:
                existing_record = cls.objects.get(source=source, time__gt=time_threshold, channel=channel, account=account)
                if text != '' and existing_record.text != '':
                    new_record = cls(chat_id=chat_id, source=source, time=timezone.now(), time_stringify=time_stringify, data=data, text=text, photo=photo, channel=channel, account=account)
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
            new_record = cls(chat_id=chat_id, source=source, time=timezone.now(), time_stringify=time_stringify, data=data, text=text, photo=photo, channel=channel, account=account)
            new_record.save()
            record_id = new_record.id
        except MultipleObjectsReturned:
            existing_record = cls.objects.filter(source=source, time__gt=time_threshold).first()
            if text != '' and existing_record.text != '':
                new_record = cls(chat_id=chat_id, source=source, time=timezone.now(), time_stringify=time_stringify, data=data, text=text, photo=photo, channel=channel, account=account)
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
        # try:
        #     existing_record = cls.objects.get(source=source, time__gt=time_threshold)
        #     if text != '' and existing_record.text != '':
        #         new_record = cls(chat_id=chat_id, source=source, time=timezone.now(), time_stringify=time_stringify, data=data, text=text, photo=photo)
        #         new_record.save()
        #     else:
        #         existing_record.data += "|||" + data
        #         existing_record.text += text
        #         if photo != "None":
        #             existing_record.photo = photo
        #         existing_record.save()
        # except MyModel.DoesNotExist:
        #     print("DoesNotExist")
        #     print(time_threshold)
        #     print(chat_id)
        #     print(source)
        #     new_record = cls(chat_id=chat_id, source=source, time=timezone.now(), time_stringify=time_stringify, data=data, text=text, photo=photo)
        #     new_record.save()
        # except Exception as e:
        #     print(f"ERROR WHILE SAVING POST TO DB: {e}")


        # instance, created = MyModel.objects.get_or_create(
        #     chat_id=chat_id,
        #     source=source,
        #     defaults={
        #         'time_stringify': time_stringify,
        #         'data': data,
        #         'text': text,
        #         'photo': photo
        #     }
        # )

        # if data != "None" and not created:
        #     print("NOT CREATED")
        #     instance.data += "|||" + data
        #     instance.text += text
        #     instance.save()

    @classmethod
    def get_sorted_records(cls, channel=None, account="first"):
        if channel is None:
            return cls.objects.filter(account=account).order_by('-time')
        return cls.objects.filter(channel=channel, account=account).order_by('-time')
        
    @classmethod
    def get_categories(cls, account="first"):
        return cls.objects.filter(account=account).values('channel').distinct()
        
    @classmethod
    def get_record_by_id(cls, record_id):
        try:
            record = cls.objects.get(id=record_id)
            return record
        except cls.DoesNotExist:
            return None


    @classmethod
    def get_news_info(cls, n_days):
        today = timezone.now()
        start_date = today
        date_range = (start_date, today)

        # Получаем записи за n дней
        news_records = cls.objects.filter(time__range=date_range).order_by('-time')

        # Группируем записи по дате
        news_info = defaultdict(list)
        for record in news_records:
            date = record.time.date()
            news_info[date].append({
                'title': record.text,
                'link': record.data,
                'photo': record.photo,
            })

        # Возвращаем информацию о новостях
        return news_info