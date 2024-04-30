from django.shortcuts import render
from .base import BaseEndpoint, Get, BaseFormEndpoint
from .utils import get_channel, get_channels, edit_channel
from panel.forms import ChannelData, ChannelEditor


class ChannelsList(Get, BaseEndpoint):
    def handle_request(self):
        context = {
            "enumerated_channels": [
                (i+1, channel) 
                for i, channel 
                in enumerate( 
                    get_channels(rights=self.current_project)
                )
            ]
        }
        return render(self.request, 'adminpanel/channels.html', context)
        
class ChannelInfo(Get, BaseFormEndpoint):
    form_template = ChannelData

    def handle_request(self):
        channel_id = self.request.GET.get('id', None)
        channel = get_channel(channel_id=channel_id)
        channel.update(Id=channel_id)
        context = {"channel": channel}
        return render(self.request, 'adminpanel/edit_channel.html', context)

class EditChannel(Get, BaseFormEndpoint):
    form_template = ChannelEditor

    def handle_request(self):
        edit_channel(
            self.request.GET.get('id'), 
            self.request.GET.get('type'), 
            project=self.current_project
        )
        return self.OK()
    
