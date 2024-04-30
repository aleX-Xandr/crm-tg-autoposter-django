from abc import ABC, abstractmethod
from aiohttp import ClientSession
from Config import get_channels_info, SERVER_URI


class Event(ABC):
    projects: str = str()
    _validations: list
    event_type: type

    def __init__(self, event) -> None:
        self.event = event

    @property
    def message(self):
        return self.event.message

    async def is_valid(self) -> bool:
        for validate in self._validations:
            if not await validate():
                return False
        return True
    
    async def validate_event_type(self):
        return isinstance(self.event, self.event_type)

    async def validate_chat(self):
        channel_data = get_channels_info(self.event.chat_id)

        if not channel_data or channel_data["Work"] != "True":
            return False
        
        self.projects = ",".join([proj for proj in channel_data["Auto_Post"]])
        return True

    @abstractmethod
    async def process(self):
        ...

    async def handle(self) -> bool:
        if not await self.is_valid():
            return False
        await self.process()
        return True
    
    async def call_api(self, path: str, json: dict) -> dict | None:
         async with ClientSession() as cs:
            async with cs.post(SERVER_URI+path, json=json) as response:
                text = await response.text()
                print(f"{path}: {text[:70]}")
                return await response.json()