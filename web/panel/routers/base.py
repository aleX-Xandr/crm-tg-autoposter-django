from abc import ABC, abstractmethod
from accounts.models import UserDatabase
from django.forms import Form
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect
from typing import Optional
import json

class Get:
    method="GET"

class Post:
    method="POST"

class Del:
    method="DELETE"

class BaseResponse:
    def OK(self, **kwargs) -> JsonResponse:
        return JsonResponse(
            {"status": "success", **kwargs}, 
            status=200
        )

    def BAD(self, **kwargs) -> JsonResponse:
        return JsonResponse(
            {"status": "bad request", **kwargs}, 
            status=400
        )
    
    def FORBIDDEN(self) -> JsonResponse:
        return JsonResponse({"status": "forbidden"}, status=403)
    
    def UNAUTHORIZED(self) -> HttpResponseRedirect:
        return redirect('accounts:login')
    

class BaseEndpoint(ABC, BaseResponse):
    method: Optional[str] = None
    request: HttpRequest
    
    def __init__(self, request: HttpRequest) -> None:
        self.request = request

    def get_user_permissions(self) -> list[str]:
        user = UserDatabase.get_record_by_login(
            self.request.COOKIES.get('username')
        )
        return user.rights.split(",") if user else []
    
    @property
    def is_valid(self) -> bool:
        if self.request.method != self.method:
            return self.BAD(err=f"{self.request.method} method is not allowed")
        elif not self.request.user.is_authenticated:
            return self.UNAUTHORIZED()
        elif not self.has_rights():
            return self.FORBIDDEN()

    @property
    def current_project(self) -> str | None:
        get_project = lambda r: r.COOKIES.get('access') or r.GET.get('access')
        return get_project(self.request)

    def has_rights(self) -> bool:
        if (rights := self.get_user_permissions()):
            return self.current_project in rights
        return False

    @abstractmethod
    def handle_request(self) -> HttpResponse:
        """
        Must be overwritten for processing the request
        """
        pass
    
    def response_middleware(self, *args, **kwargs) -> None:
        """
        Can be overwritten for modifying response
        """
        pass
    
    @classmethod
    def router(cls, request) -> HttpResponse:
        obj = cls(request=request)
        if (error := obj.is_valid):
            return error
        result = obj.handle_request()
        obj.response_middleware(result)
        return result
    


class BaseFormEndpoint(BaseEndpoint):
    form: Optional[Form] = None
    form_template: Form

    def validate_form(self) -> bool:
        data = getattr(self.request, self.method)
        self.form = self.form_template(data)
        return self.form.is_valid()

    @property
    def is_valid(self) -> bool:
        if self.request.method != self.method:
            return self.BAD(err="method not allowed")
        elif not self.request.user.is_authenticated:
            return self.UNAUTHORIZED()
        elif not self.has_rights():
            return self.FORBIDDEN()
        elif not self.validate_form():
            return self.BAD(err=f"invalid arguments {self.form.data}")

class BaseAPI(Post, BaseFormEndpoint):

    @property
    def is_valid(self) -> bool:
        if self.request.method != self.method:
            return self.BAD(err="method not allowed")
        elif not self.validate_form():
            return self.BAD(err=f"invalid arguments {self.form.data}")
        # return (
        #     self.request.method == self.method and self.validate_form()
        # )

    def validate_form(self) -> bool:
        if self.method == "POST":
            data = json.loads(self.request.body.decode('utf-8'))
            self.form = self.form_template(data)
        else:
            data = {}
            for key, value in self.request.GET.lists():
                data[key] = value if len(value) > 1 else value[0]
            self.form = self.form_template(data)
            print(self.form.is_valid())
        return self.form.is_valid()
    
