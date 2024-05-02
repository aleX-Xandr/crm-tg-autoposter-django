import mimetypes
import logging, json
import datetime, os
from loader import client, web_socket
import handlers
import asyncio, aiohttp
from aiohttp import web
from telethon.tl import types, functions
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from Config import get_projects_info
from telethon.errors.rpcerrorlist import MediaEmptyError


logging.basicConfig(format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
                    level=logging.INFO)

def check_time(datetime_str):
    if datetime_str != "now" and not datetime_str is None:
        datetime_obj = datetime.datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M")
        current_datetime = datetime.datetime.now()
        if datetime_obj > current_datetime:
            return False
        else:
            return True
    else:
        return True

def add_to_json(title,operator,options,invite_link,project,flags=""):
    if operator:
        id_channel = "-100" + str(title.chats[0].id)
        title_channel = title.chats[0].title
    else:
        id_channel = "-100"+str(title.id)
        title_channel = title.title
    with open('file.json', encoding='utf8') as f: 
        data = json.load(f) 
        if str(id_channel) in data:
            if project in data[str(id_channel)]["Auto_Post"]:
                return
            data[str(id_channel)]["Auto_Post"][project] = "False"
        else:
            data[str(id_channel)]={"Group_Name":title_channel,"Work":"True","Type":options,"Auto_Post":{project:"False"},"Invite_link":invite_link, "flags":flags}
    with open('file.json', 'w', encoding='utf8') as outfile: 
        json.dump(data, outfile, ensure_ascii=False, indent=2) 

async def handle_task():
    i = 720
    while True:
        i += 1
        if i >= 720 :
            i = 0
            for directory_path in ["/home/net-parse-hub/src/web/media", "/home/net-parse-hub/src/web/static/img/tg_files", "/home/net-parse-hub/src/web/static/img/tg_photos"]:

                current_time = datetime.datetime.now()

                one_week_ago = current_time - datetime.timedelta(weeks=1)

                for root, dirs, files in os.walk(directory_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
                        
                        if file_creation_time < one_week_ago:
                            try:
                                os.remove(file_path)  
                                print(f"Удалено: {file_path}")
                            except Exception as e:
                                print(f"Ошибка при удалении файла {file_path}: {e}")

            print("Операция завершена.")
        if i % 2 == 0:
            try:
                with open("file_new_channel.json", encoding="utf8") as f: 
                    data = json.load(f)

                new_data = {
                    "new": []
                }
                old_data = {
                    "new": []
                }
                if not "new" in data:
                    data["new"] = []
                for new_chat in data["new"]:
                    invite_link = new_chat["invite_link"]
                    project = new_chat["project"]
                    flags = new_chat["flags"]
                    message = invite_link.split("/")[-1].replace("+","")
                    async with client:
                        try:
                            title = await client(JoinChannelRequest(message))
                            add_to_json(title,True,options="Channel",invite_link = invite_link, project=project, flags=flags)
                        except Exception as e:
                            if str(e) == "You have successfully requested to join this chat or channel (caused by ImportChatInviteRequest)":
                                add_to_json(res,False,options="Channel",invite_link = invite_link, project=project, flags=flags)
                                return
                            try:
                                title = await client(ImportChatInviteRequest(message))
                                res = await client.get_entity(invite_link)
                                if isinstance(res, types.Channel):
                                    add_to_json(title,True,options="Channel",invite_link = invite_link, project=project, flags=flags)
                                else:
                                    add_to_json(title,True,options="Chat",invite_link = invite_link, project=project, flags=flags)     
                            except Exception as e:
                                if str(e) == "You have successfully requested to join this chat or channel (caused by ImportChatInviteRequest)":
                                    add_to_json(res,False,options="Channel",invite_link = invite_link, project=project, flags=flags)
                                    return
                                if str(e) == "The authenticated user is already a participant of the chat (caused by ImportChatInviteRequest)":
                                    res = await client.get_entity(invite_link)
                                    if isinstance(res, types.Channel):
                                        add_to_json(res,False,options="Channel",invite_link = invite_link, project=project, flags=flags)
                                    else:
                                        add_to_json(res,False,options="Chat",invite_link = invite_link, project=project, flags=flags)  
                                else:
                                    print(f"ERROR WHILE JOINING CHANNEL: {e}\nLINK:{invite_link}")
                                    new_data["new"].append([invite_link, str(e)])
                with open('file_new_channel_errors.json', 'w', encoding='utf8') as f: 
                    json.dump(new_data, f, ensure_ascii=False, indent=2) 

                with open('file_new_channel.json', 'w', encoding='utf8') as f: 
                    json.dump(old_data, f, ensure_ascii=False, indent=2) 
            except Exception as e:
                print(e)
###################################################
        # await asyncio.sleep(5)        #   DELAY   #
###################################################
        try:
            with open("parser_bot\posts_to_send.json", encoding="utf8") as f: 
                data = json.load(f)
            if "new" not in data:
                continue
            new_data = {
                "new": []
            }
            old_data = {
                "new": []
            }
            changed = False
            for post_data in data["new"]:
                
                if check_time(post_data["time"]):
                    if len(post_data["text"]) > 900:
                        post_data["text"] = post_data["text"][:900] + "..."
                    try:
                        project = get_projects_info(post_data["project"])
                        if not project:
                            print("NOT PROJECT")
                            continue
                        CHAT_ID = int(project["id"])
                        
                        CHANNEL_LINK = project["link"]

                        print(CHAT_ID, CHANNEL_LINK)
                        if not (post_data["data"] is None or post_data["data"] in ["None", ""]):
                            print(2)
                            await client.send_file(CHAT_ID, ["../web/"+path for path in post_data["data"].split("|||") if path != "None"], caption=post_data["text"]+CHANNEL_LINK) #, link_preview = True if "https://cutt.ly" in post_data["text"] else False)
                        elif not (post_data["photo"] is None or post_data["photo"] in ["None", ""]):
                            try:
                                print(3)
                                await client.send_file(CHAT_ID, post_data["photo"], caption=post_data["text"]+CHANNEL_LINK) #, link_preview = True if "https://cutt.ly" in post_data["text"] else False)
                            except MediaEmptyError:
                                async with aiohttp.ClientSession() as session:
                                    async with session.get(post_data["photo"]) as response:
                                        if response.status == 200:
                                            file_data = await response.read()
                                            print(4)
                                            await client.send_file(CHAT_ID, file_data, caption=post_data["text"]+CHANNEL_LINK) #, link_preview = True if "https://cutt.ly" in post_data["text"] else False)
                                        else:
                                            print("CANT DOWNLOAD MEDIA main.py")
                            except Exception as e:
                                print(type(e))
                                raise e
                        else:
                            print(5)
                            await client.send_message(CHAT_ID, post_data["text"]+CHANNEL_LINK) #, link_preview = True if "https://cutt.ly" in post_data["text"] else False)
                        changed = True
                    except Exception as e:
                        print(f"ERROR handle_task (main.py): {e}")
                        if " seconds is required (caused by " in str(e):
                            print("Sleepping:", int(str(e).split(" ")[3]))
                            await asyncio.sleep(int(str(e).split(" ")[3]))
                        new_data["new"].append([post_data, str(e)])
                    finally:
                        continue
                else:
                    old_data["new"].append(post_data)
            if changed:
                with open("posts_to_send.json", "w", encoding="utf8") as f: 
                    json.dump(old_data, f, ensure_ascii=False, indent=2)
            if new_data["new"]:
                with open("posts_to_send_errors.json", "w", encoding="utf8") as f: 
                    json.dump(new_data, f, ensure_ascii=False, indent=2) 
        except Exception as e:
            print(e)


async def main():
    # loop = asyncio.get_event_loop()
    # loop.create_task(handle_task())
    # await asyncio.sleep(10000)
    await web_socket.connect()

if __name__ == "__main__":
    asyncio.run(main())
    # client.start()
    # executor.start_polling(dp)
    # client.run_until_disconnected()

