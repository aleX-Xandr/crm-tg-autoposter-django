import json
from .models import MyModel
from accounts.models import UserDatabase

# MyModel.objects.filter(text='').delete()
# MyModel.objects.all().delete()
# UserDatabase.objects.all().delete()

#######################################################################################################################

def get_channel(channel_id=None):
    with open('../../../parser_bot/file.json', encoding='utf8') as f: 
        data = json.load(f)
    new_data = []
    for key, value in data.items():
        if channel_id:
            if channel_id != key:
                continue
            value["Id"] = key
            new_data = value
        else: 
            value["Id"] = key
            new_data.append(value)
    return new_data

def add_channel(channel_link=None):
    try:
        with open('../../../parser_bot/file_new_channel.json', encoding='utf8') as f: 
            data = json.load(f)
        if not "new" in data:
            data["new"] = []
        data['new'].append(channel_link)
        with open('../../../parser_bot/file_new_channel.json', 'w', encoding='utf8') as f: 
            json.dump(data, f, ensure_ascii=False, indent=2) 

        return True
    except Exception as e:
        print(f"Error in function 'utils.add_channel': {e}")
        return False

def edit_channel(channel_id, Auto_Post):
    try:
        with open('../../../parser_bot/file.json', encoding='utf8') as f: 
            data = json.load(f)
        print("channel_id in data", channel_id in data)
        print([ ch for ch in data], channel_id)
        if channel_id in data:
            data[channel_id]["Auto_Post"] = "False" if Auto_Post == "True" else "True"
            with open('../../../parser_bot/file.json', 'w', encoding='utf8') as f: 
                json.dump(data, f, ensure_ascii=False, indent=2) 


    except Exception as e:
        print(f"Error in function 'utils.edit_channel': {e}")

def delete_channel(channel_link=None):
    try:
        with open('../../../parser_bot/file.json', encoding='utf8') as f: 
            data_file = json.load(f)
        new_data = {}
        for channel, data in data_file.items():
            if channel_link == data["Invite_link"] or channel_link in data["Invite_link"]:
                del data_file[channel]
                break
        with open('../../../parser_bot/file.json', 'w', encoding='utf8') as f: 
            json.dump(data_file, f, ensure_ascii=False, indent=2) 

        return True
    except Exception as e:
        print(f"Error in function 'utils.delete_channel': {e}")
        return False

#######################################################################################################################

def get_site(site_id=None):
    with open('../../../parser_bot/file_new_site.json', encoding='utf8') as f: 
        data = json.load(f)
        print(data)
    new_data = []
    for value in data['new']:
        if site_id:
            if site_id != value:
                continue
            new_data = {
                "name": value.split("/")[2],
                "url": value
            }
        else: 
            new_data.append({
                "name": value.split("/")[2],
                "url": value
            })
    return new_data

def add_site(site_link=None):
    try:
        with open('../../../parser_bot/file_new_site.json', encoding='utf8') as f: 
            data = json.load(f)
        if "new" not in data:
            data['new'] = [];
        data['new'].append(site_link)
        with open('../../../parser_bot/file_new_site.json', 'w', encoding='utf8') as f: 
            json.dump(data, f, ensure_ascii=False, indent=2) 

        return True
    except Exception as e:
        print(f"Error in function 'utils.add_site': {e}")
        return False

def delete_site(site_link=None):
    try:
        with open('../../../parser_bot/file_new_site.json', encoding='utf8') as f: 
            data = json.load(f)
        if "new" not in data:
            data['new'] = [];
        else:
            data['new'].remove(site_link)
        with open('../../../parser_bot/file_new_site.json', 'w', encoding='utf8') as f: 
            json.dump(data, f, ensure_ascii=False, indent=2) 

        return True
    except Exception as e:
        print(f"Error in function 'utils.delete_site': {e}")
        return False

#######################################################################################################################

def add_post(payload):
    try:
        res = MyModel.add_or_update_record(payload['chat_id'], payload['time_stringify'], payload['text'], payload['source'], payload['data'], payload['photo'], payload['channel'], payload['account'])
        return res
    except Exception as e:
        print(f"Error in function 'utils.add_post': {e}")
        return e

def update_post(payload):
    try:
        res = MyModel.update_record(payload['id'], payload['text'])
        return res
    except Exception as e:
        print(f"Error in function 'utils.update_post': {e}")
        return False

def update_post_data(post_id, data):
    data = [file.replace("http://134.209.195.23:8000/", "") for file in data]
    data = "|||".join(data)
    try:
        res = MyModel.update_data(post_id, data)
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
        with open('../../../parser_bot/posts_to_send.json', encoding='utf8') as f: 
            data = json.load(f)
        if "new" not in data:
            data['new'] = [];
        data['new'].append(post_data)
        with open('../../../parser_bot/posts_to_send.json', 'w', encoding='utf8') as f: 
            json.dump(data, f, ensure_ascii=False, indent=2) 
        MyModel.delete_old()
        return True
    except Exception as e:
        print(f"Error in function 'utils.send_post': {e}")
        return False

#######################################################################################################################

def get_news(channel, request):
    try:
        print(request.COOKIES)
        user = UserDatabase.get_record_by_login(request.COOKIES.get('username'))
        if user is None:
            print("USER IS NONE")
            rights = "first"
        else:
            print("USER IS NOT NONE", user.rights)
            rights = user.rights
        result = MyModel.get_sorted_records(channel, rights)
        return result
    except Exception as e:
        print(f"Error in function 'utils.get_news': {e}")
        return False

def get_news_categories(request):
    try:

        user = UserDatabase.get_record_by_login(request.COOKIES.get('username'))
        if user is None:
            rights = "first"
        else:
            rights = user.rights
        result = MyModel.get_categories(rights)
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
