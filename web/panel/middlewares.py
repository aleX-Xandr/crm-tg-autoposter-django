from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from accounts.models import UserDatabase


class AuthMiddleware(AuthenticationMiddleware):
    def process_request(self, request):
        response = super().process_request(request)

        # if not request.user.is_authenticated:
        #     return HttpResponseRedirect('/auth/login/')

        user = UserDatabase.get_record_by_login(request.COOKIES.get('username'))
        # if not user:
        #     return HttpResponseRedirect('/panel/dashboard')

        request.META['user'] = user

        return response
