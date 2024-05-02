from channels.generic.websocket import AsyncWebsocketConsumer

class WebSocket(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "websocket"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        print(close_code)
        pass

    async def send_post(self, event):
        await self.send(text_data=str(event['send_post']))

    async def add_site(self, event):
        await self.send(text_data=str(event['site_info']))

    async def stop_parser(self, event):
        await self.send(text_data=str(event['site_info']))