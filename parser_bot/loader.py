from Config import api_hash,api_id, TOKEN_BOT
from telethon import TelegramClient, events
from aiogram import Bot, types
from web_socket import WebSocketClient
#Roman

# bot = Bot(token=TOKEN_BOT,parse_mode=types.ParseMode.HTML)
# storage = MemoryStorage()   
# dp = Dispatcher(bot,storage=storage)
web_socket = WebSocketClient("ws://127.0.0.1:8000/ws")

# client = TelegramClient('anon1_mode=rwc&timeout=60', api_id, api_hash)
# client.parse_mode = 'html'

client = ""