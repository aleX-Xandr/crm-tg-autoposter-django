from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned

def change_user_password_by_login(login, new_password):
    User = get_user_model()
    
    try:
        user = User.objects.get(username=login)
        user.set_password(new_password)
        user.save()
        return True
    except User.DoesNotExist:
        return False

def delete_user_by_login(login, password):
    User = get_user_model()
    
    try:
        print("one record try")
        user = User.objects.filter(username=login).delete()
        return True
    except User.DoesNotExist:
        return False
    except MultipleObjectsReturned:
        print("multiple records")
        user = User.objects.filter(username=login).delete()
        return True

class UserDatabase(models.Model):
    id = models.BigAutoField(primary_key=True)
    login = models.TextField(default='')
    password = models.TextField(default='')
    rights = models.TextField(default='')
    comment = models.TextField(default='')
    favourites = models.TextField(default='')

    @classmethod
    def update_favourites(cls, login, favourites):
        try:
            existing_record = cls.objects.get(login=login)
            existing_record.favourites = favourites
            existing_record.save()
        except Exception as e:
            print(f"ERROR WHILE UPDATING DB: {e}")

    @classmethod
    def add_or_update_record(cls, login, password, rights=""):
        try:
            existing_record = cls.objects.get(login=login)
            existing_record.password = password
            existing_record.save()
        except cls.DoesNotExist:
            print("DoesNotExist")
            new_record = cls(login=login, password=password, rights=rights)
            new_record.save()
        except Exception as e:
            print(f"ERROR WHILE SAVING POST TO DB: {e}")

    @classmethod
    def get_record_by_login(cls, val, type_val="login"):
        try:
            if type_val == "login":
                record = cls.objects.get(login=val)
            else:
                record = cls.objects.get(id=val)

            print(record)
            return record
        except cls.DoesNotExist:
            return None
        except MultipleObjectsReturned:
            if type_val == "login":
                record = cls.objects.filter(login=val).first()
            else:
                record = cls.objects.filter(id=val).first()
        print(record)
        return record

    @classmethod
    def update_user(cls, userid, rights, comment):
        try:
            user = cls.objects.get(id=userid)
        except cls.DoesNotExist:
            return False
        except Exception as e:
            print(e)
            return False
        user.rights = rights
        user.comment = comment
        user.save()
        return True
        
    @classmethod
    def update_pass(cls, login, password):
        try:
            user = cls.objects.get(login=login)
            user.password = password
            user.save()
            return True
        except cls.DoesNotExist:
            return False
        except Exception as e:
            print(e)
            return False
        
    @classmethod
    def delete_user(cls, login):
        try:
            user = cls.objects.filter(login=login).delete()
            return True
        except cls.DoesNotExist:
            return False
        except MultipleObjectsReturned:
            user = cls.objects.filter(login=login).delete()
            return True

    @classmethod
    def get_sorted_records(cls):
        return cls.objects.all().order_by('login')

# Create your models here.
class UserAccount(AbstractUser):
    id = models.AutoField(primary_key=True)
    admin = models.CharField(max_length=255, default="")

    def __str__(self):
        return str(super().username)

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__, 
            ', '.join([
                f'{key}={value}'
                for key, value in self.__dict__['__values__'].items()
            ])
        )

    def get_admin_status(self):
        return self.admin