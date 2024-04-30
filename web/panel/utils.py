import json
from .models import MyModel, parser_site
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# MyModel.objects.filter(text='').delete()
# MyModel.objects.all().delete()
# UserDatabase.objects.all().delete()

#######################################################################################################################

def get_channel(channel_id=None, rights="first") -> dict | None:
    with open('parser_bot/file.json', encoding='utf8') as f: 
        data = json.load(f)
    if channel_id in data:
        channel_data = data[channel_id]
        channel_data["IsAutoPosted"] = rights in channel_data["Auto_Post"]
        return data[channel_id]
    

def get_channels(rights="first") -> list:
    with open('parser_bot/file.json', encoding='utf8') as f: 
        data = json.load(f)
    new_data = []
    for key, value in data.items():
        autopost_data = value["Auto_Post"]
        if rights in autopost_data:
            value["Id"] = key
            new_data.append(value)
    return new_data

def add_channel(channel_link=None, project="first", flags=""):
    try:
        with open('parser_bot/file_new_channel.json', encoding='utf8') as f: 
            data = json.load(f)
        if not "new" in data:
            data["new"] = []
        data['new'].append({"invite_link":channel_link, "project": project, "flags":flags})
        with open('parser_bot/file_new_channel.json', 'w', encoding='utf8') as f: 
            json.dump(data, f, ensure_ascii=False, indent=2) 

        return True
    except Exception as e:
        print(f"Error in function 'utils.add_channel': {e}")
        return False

def edit_channel(channel_id, Auto_Post, project="first"):
    try:
        with open('parser_bot/file.json', encoding='utf8') as f: 
            data = json.load(f)
        print("channel_id in data", channel_id in data)
        print([ ch for ch in data], channel_id)
        if channel_id in data:
            data[channel_id]["Auto_Post"][project] = "False" if Auto_Post == "True" else "True"
            with open('parser_bot/file.json', 'w', encoding='utf8') as f: 
                json.dump(data, f, ensure_ascii=False, indent=2) 


    except Exception as e:
        print(f"Error in function 'utils.edit_channel': {e}")

def delete_channel(channel_link=None, project="first", flags=""):
    try:
        with open('parser_bot/file.json', encoding='utf8') as f: 
            data_file = json.load(f)
        new_data = {}
        for channel, data in data_file.items():
            if channel_link == data["Invite_link"] or channel_link in data["Invite_link"]:
                if project in data["Auto_Post"]:
                    if len(data["Auto_Post"]) == 1:
                        del data_file[channel]
                    else:
                        del data_file[channel]["Auto_Post"][project]
                    break
        else:
            return False
        with open('parser_bot/file.json', 'w', encoding='utf8') as f: 
            json.dump(data_file, f, ensure_ascii=False, indent=2) 

        return True
    except Exception as e:
        print(f"Error in function 'utils.delete_channel': {e}")
        return False

#######################################################################################################################

def get_site(rights=""):
    with open('parser_bot/file_new_site.json', encoding='utf8') as f: 
        data = json.load(f)
    new_data = []
    for site in data['new']:
        value = site["link"]
        project = site["project"]
        if project == rights:
            new_data.append({
                "name": value.split("/")[2],
                "url": value
            })
    return new_data



def add_site(site_link:str, project="first", flags="", use_proxy = False):
    try:
        if not any(rss in site_link for rss in ['/rss', '/feed']):
            return False
        if not parser_site.create_record(url=site_link,project=project, use_proxy=False, type="RSS"):
            return False
        data = {
            "type": "add_site",
            "site_info": {"url":site_link, 
                            "project":project, 
                            "use_proxy":use_proxy, 
                            "type":"RSS",
                            "type_answer":"add_site"}
        }
        async_to_sync(get_channel_layer().group_send)("websocket", data)
        return True
    except Exception as E:
        pass
def delete_site(site_link=None, project="first", flags=""):
    try:
        if not parser_site.delete_record(url=site_link, project=project):
            return False
        
        data = {
            "type": "stop_parser",
            "site_info": {"url":site_link,
                          "type_answer":"stop_parser"}
        }
        async_to_sync(get_channel_layer().group_send)("websocket", data)
        return True
    except Exception as e:
        print(f"Error in function 'utils.delete_site': {e}")
        return False

#######################################################################################################################

def add_post(payload):
    try:
        MyModel.delete_old()
        return MyModel.add_or_update_record(**payload)
    except Exception as e:
        print(f"Error in function 'utils.add_post': {e}")
        return e

def update_post(payload): # TODO DELETE
    try:
        res = MyModel.update_text(id=payload['id'], text=payload['text'])
        return res
    except Exception as e:
        print(f"Error in function 'utils.update_post': {e}")
        return False

def update_post_data(post_id, data):
    data = [file.replace("http://134.209.195.23:8000/", "") for file in data]
    data = "|||".join(data)
    try:
        res = MyModel.update_data(id=post_id, data=data)
        return res

    except Exception as e:
        print(f"Error in function 'utils.update_post_data': {e}")

def delete_post(payload):
    try:
        res = MyModel.delete_record(payload['id'])
        return res
    except Exception as e:
        print(f"Error in function 'utils.delete_post': {e}")
        return False

def send_post(post_data):
    try:
        with open('parser_bot/posts_to_send.json', encoding='utf8') as f: 
            data = json.load(f)
        if "new" not in data:
            data['new'] = [];
        data['new'].append(post_data)
        with open('parser_bot/posts_to_send.json', 'w', encoding='utf8') as f: 
            json.dump(data, f, ensure_ascii=False, indent=2) 
        return True
    except Exception as e:
        print(f"Error in function 'utils.send_post': {e}")
        return False

#######################################################################################################################

# def get_news(channel, rights):
#     try:
        
#         result = MyModel.get_sorted_records(channel, rights)
#         return result
#     except Exception as e:
#         print(f"Error in function 'utils.get_news': {e}")
#         return False

def get_news_categories(rights):
    try:
        result = MyModel.get_categories(rights)
        print(result)
        return result.reverse()
    except Exception as e:
        print(f"Error in function 'utils.get_news_categories': {e}")
        return False

def get_newsletter(newsletter_id, number_flag = True):
    try:
        result = MyModel.objects.get(id=newsletter_id)
        if number_flag:
            if result.data != '' and result.data != 'None' :
                result.data = len(result.data.split("|||"))
            else:
                result.data = 0
        return result

    except Exception as e:
        print(f"Error in function 'utils.get_newsletter': {e}")
        return False

#######################################################################################################################
