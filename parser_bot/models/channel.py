from aiohttp import ClientSession
from asyncio import sleep, create_task
from Config import get_projects_info, SERVER_URI
from datetime import datetime
from models.base import Event
from loader import client
from telethon.events import NewMessage, MessageDeleted
from telethon.tl.functions.messages import GetMessagesViewsRequest
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, InputPeerChannel


class ChannelValidator(Event):

    def __init__(self, event):
        super().__init__(event)
        self._validations = [
            self.validate_event_type, 
            self.is_channel, 
            self.check_own_channel, 
            self.validate_chat
        ]

    async def is_channel(self):
        return self.event.is_channel
    
    @property
    def chat_id(self):
        if self.event.chat:
            return self.event.chat.id
        full_chat_id = str(self.event.chat_id)
        return int(full_chat_id.replace("-100", "")
        )

    async def check_own_channel(self) -> bool:
        for project in get_projects_info():
            if self.event.chat_id == project["id"]:
                if self.message.message and "Пiдписатися" not in self.message.message:
                    await client.edit_message(
                        self.message, 
                        self.message.text + project["link"]
                    )
                return False
        return True


class ChannelPostDeleted(ChannelValidator):
    event_type = MessageDeleted.Event

    async def process(self):
        return await self.call_api(
            path="panel/update_post_category/",
            json={
                "chat_id":  f"https://t.me/c/{self.chat_id}/{self.event.deleted_id}",
                "category": "channel_post:deleted"
            }
        )


class ChannelPostCreated(ChannelValidator):
    event_type = NewMessage.Event
    file_path: str = "None"
    photo_url: str = "None"
    last_log: dict = {}

    @property
    def is_document(self):
        return isinstance(self.message.media, MessageMediaDocument)

    @property
    def is_photo(self):
        return isinstance(self.message.media, MessageMediaPhoto)

    async def download_media(self) -> None:
        path = await self.message.download_media(
            file="../web/static/img/tg_files"
        ) # full path
        self.file_path = path.split("/web/", 1)[1] # relational path right from "web" folder name

    async def download_media_thumb(self) -> None:
        res_thumb = await self.message.download_media(
            file="../web/static/img/tg_photos", 
            thumb=1
        ) # full path
        thumb_path = res_thumb.split("/web/", 1)[1] # relational path right from "web" folder name
        self.photo_url = SERVER_URI+thumb_path

    async def get_last_msgs_id(self):
        response = await self.call_api(
            path="panel/get_last_msgs_id/",
            json={"partial_chat_id": f"https://t.me/c/{self.chat_id}/"}
        )
        return response.get("result", [])

    async def add_post(self):
        return await self.call_api(
            path="panel/add_post/",
            json={
                "account":  self.projects,
                "channel":  self.event.chat.title, 
                "chat_id":  f"https://t.me/c/{self.chat_id}/{self.event.id}",
                "data":     self.file_path,
                "photo":    self.photo_url,
                "source":   self.event.chat.title,
                "text":     self.message.raw_text,
                "time_stringify": str(self.event.date),
                "views":    self.event.message.views or 0
            }
        )

    async def update_post(self, **payload: dict):
        return await self.call_api(
            path="panel/update_post_views/", 
            json=payload
        )

    async def update_views(self, delay: int):
        await sleep(delay)
        try:
            if self.event.input_chat is None:
                current_datetime = datetime.now()
                with open(f"""{current_datetime.strftime("%Y-%m-%d_%H-%M-%S.txt")}""", "w", encoding="utf-8") as f:
                    f.write(f"NO INPUT_CHAT: {self.event.chat.title}, {self.event}")
                return
            # print("INPUT_CHAT: ", self.event.input_chat)
            
            last_msgs_id = await self.get_last_msgs_id()
            id_list = [
                int(row["chat_id"].split("/")[-1]) 
                for row in last_msgs_id
            ]
            print("UPDATE VIEWS ID: ", id_list)
            messages = await client(GetMessagesViewsRequest(
                peer=self.event.input_chat, 
                id=id_list,
                increment=False,
            ))
            for i, message_data in enumerate(messages.views):
                if message_data.views == last_msgs_id[i]["views"]:
                    # print("No views changed ", message_data.views, "|", last_msgs_id[i]["views"])
                    continue
                await self.update_post(
                    chat_id=f"https://t.me/c/{self.chat_id}/{id_list[i]}", 
                    views=message_data.views
                )
        except Exception as e:
            print("UPDATE VIEWS ERROR", self.event.input_chat, self.event.chat, e)

    async def process(self):
        try:
            if self.message.media:
                if self.is_photo:
                    await self.download_media()
                    await self.download_media_thumb()
                elif self.is_document:
                    await self.download_media()
                else:
                    return
                if self.message.message == "":
                    await sleep(1)
            elif self.message.message == "":
                return
            await self.add_post()
            create_task(self.update_views(60*2))
            create_task(self.update_views(60*15))
            # create_task(self.update_views(60*60))
            # create_task(self.update_views(60*60*24))
        except Exception as e:
            print(f"Error while adding post: {e}")