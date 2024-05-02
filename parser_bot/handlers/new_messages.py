# from models.channel import ChannelPostCreated, ChannelPostDeleted
# from loader import client
# from telethon import events

# format_media = []

# @client.on(events.NewMessage)
# async def created_channel_post(event):
#     processor = ChannelPostCreated(event)
#     await processor.handle()

# @client.on(events.MessageDeleted)
# async def deleted_channel_post(event):
#     processor = ChannelPostDeleted(event)
#     await processor.handle()
    
