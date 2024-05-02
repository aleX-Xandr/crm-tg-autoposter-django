from aiogram import Bot
from aiogram.enums import ParseMode
from Config import TOKEN_BOT, get_projects_info
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import FSInputFile
from urllib.parse import urlparse

class SenderPost:
    bot:Bot = Bot(TOKEN_BOT, parse_mode=ParseMode.HTML)
    path_to_media = "web/"
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff','.webp',".jfif"]

    @classmethod
    def get_type(self, url_to_media:str):
        path = urlparse(url_to_media).path
        if any(path.lower().endswith(ext) for ext in self.image_extensions):
            return "photo"
        else:
            return "video"

    @classmethod
    async def send_post(
        cls,
        data:dict
    ):
        info_project = get_projects_info(project=data['project'])
        chat_id = info_project['id']
        
        text=data['text']+info_project['link']
        try:
            if not data['data'] and not data['photo']:
                await cls.bot.send_message(chat_id=chat_id, text=text)
            elif photo:=data['photo'] and not data['photo']:
                await cls.bot.send_photo(chat_id=chat_id,photo=photo,caption=text)
            else:
                media_group = MediaGroupBuilder(caption=text)
                media_group.add(type=cls.get_type(url_to_media=data['photo']), media=data['photo'])
                for media in data['data'].split("|||"):
                    media_group.add(type=cls.get_type(url_to_media=media), media=FSInputFile(cls.path_to_media + media))
                await cls.bot.send_media_group(chat_id=chat_id, media=media_group.build())
        except Exception as E: 
            print(E)
