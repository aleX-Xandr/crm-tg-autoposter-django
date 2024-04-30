from .base import Get, BaseEndpoint
from datetime import datetime, timedelta
from django.shortcuts import render

class Dashboard(Get, BaseEndpoint):
    def handle_request(self):
        response = render(self.request, 'adminpanel/index.html',)
        if (access := self.request.GET.get('access', None)):
            response.set_cookie('access', access, expires=datetime.now()+timedelta(days=30))
        return response
