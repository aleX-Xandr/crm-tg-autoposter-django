
import websockets
import logging
import ast
from send_posts import SenderPost

class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.websocket = None

    async def connect(self):
        while True:
            try:
                self.websocket = await websockets.connect(self.uri)
                print(f"Connected to {self.uri}")
                await self.receive_messages()
            except websockets.ConnectionClosedError:
                print("Connection to the server is closed. Reconnecting...")
            except ConnectionRefusedError:
                print("Connection was refused by the server.")
            except Exception as e:
                print(f"Error: {e}")

    
    async def receive_messages(self):
        while True:
            response = await self.websocket.recv()
            response,valide = self.validate_response(response)
            if not valide:
                logging.error(f"WEB SOCKET ERROR : {response}")
            await SenderPost.send_post(data=response)
    def validate_response(self, response):
        try:
            print(response)
            return ast.literal_eval(response), True
        except Exception as E:
            print(E)
            return False, False



