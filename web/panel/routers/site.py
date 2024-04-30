from .base import Get, BaseEndpoint
from django.shortcuts import render
from .utils import get_site

class SitesList(Get, BaseEndpoint):
    def handle_request(self):
        context = {
            "enumerated_sites": [
                (i+1, channel) 
                for i, channel 
                in enumerate( 
                    get_site(rights=self.current_project)
                )
            ]
        }
        return render(self.request, 'adminpanel/sites.html', context)
