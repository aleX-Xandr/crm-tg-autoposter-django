import json
from datetime import datetime, timedelta
from django.conf import settings
from functools import wraps
from panel.models import MyModel, parser_site


# MyModel.objects.filter(text='').delete()
# MyModel.objects.all().delete()
# UserDatabase.objects.all().delete()

#######################################################################################################################


def csrf_exempt(view_func):
    """Mark a view function as being exempt from the CSRF view protection."""

    # view_func.csrf_exempt = True would also work, but decorators are nicer
    # if they don't have side effects, so return a new function.
    @wraps(view_func)
    def wrapper_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    wrapper_view.csrf_exempt = True
    return wrapper_view

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
    return sorted(new_data, key=lambda channel: channel["Group_Name"])

def add_channel(channel_link=None, project="first"):
    try:
        with open('parser_bot/file_new_channel.json', encoding='utf8') as f: 
            data = json.load(f)
        if not "new" in data:
            data["new"] = []
        data['new'].append({"invite_link":channel_link, "project": project})
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

def delete_channel(channel_link=None, project="first"):
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
    sites = parser_site.get_all_records(project=rights)
    new_data = []
    for site in sites:
        new_data.append({
            "name":site.url.split("/")[2],
            "url":site.url
        })
    return new_data
    # with open('parser_bot/file_new_site.json', encoding='utf8') as f: 
    #     data = json.load(f)
    # new_data = []
    # for site in data['new']:
    #     value = site["link"]
    #     project = site["project"]
    #     if project == rights:
    #         new_data.append({
    #             "name": value.split("/")[2],
    #             "url": value
    #         })
    # return new_data

def add_site(site_link=None, project="first"):
    try:
        with open('parser_bot/file_new_site.json', encoding='utf8') as f: 
            data = json.load(f)
        if "new" not in data:
            data['new'] = {};
        data['new'].append({"link":site_link, "project":project})
        with open('parser_bot/file_new_site.json', 'w', encoding='utf8') as f: 
            json.dump(data, f, ensure_ascii=False, indent=2) 

        return True
    except Exception as e:
        print(f"Error in function 'utils.add_site': {e}")
        return False

def delete_site(site_link=None, project="first"):
    try:
        with open('parser_bot/file_new_site.json', encoding='utf8') as f: 
            data = json.load(f)
        if "new" not in data:
            data['new'] = [];
        for i,site_obj in enumerate(data['new']):
            print(site_link, project, site_obj["link"] == site_link, site_obj["project"] == project)
            if site_obj["link"] == site_link and site_obj["project"] == project:
                del data["new"][i]
                break
        else:
            print("ELSEEEEEEE")
            return False
        with open('parser_bot/file_new_site.json', 'w', encoding='utf8') as f: 
            json.dump(data, f, ensure_ascii=False, indent=2) 

        return True
    except Exception as e:
        print(f"Error in function 'utils.delete_site': {e}")
        return False

#######################################################################################################################

def update_post_data(post_id, files_path):
    files_path = [file.replace(f"{settings.SERVER_URI}/", "") for file in files_path]
    files_path = "|||".join(files_path)
    try:
        res = MyModel.update_data(id=post_id, data=files_path)
        return res
    except Exception as e:
        print(f"Error in function 'utils.update_post_data': {e}")
        return False
    
def send_post(post_data):
    try:
        with open('parser_bot/posts_to_send.json', encoding='utf8') as f: 
            data = json.load(f)
        if "new" not in data:
            data['new'] = []
        data['new'].append(post_data)
        with open('parser_bot/posts_to_send.json', 'w', encoding='utf8') as f: 
            json.dump(data, f, ensure_ascii=False, indent=2) 
        return True
    except Exception as e:
        print(f"Error in function 'utils.send_post': {e}")
        return False

#######################################################################################################################

def get_news(category, rights, sorting, source="", keyword="", dateFrom="", dateTo=""):
    now = datetime.now() + timedelta(days=1)
    try:
        result = MyModel.get_sorted_records(category, rights, sorting, keyword, time_range=[dateFrom or "2000-01-01", dateTo or now.strftime("%Y-%m-%d")], source=source)
        return result
    except Exception as e:
        print(f"Error in function 'utils.get_news': {e}")
        return []

def get_news_categories(rights):
    try:
        result = MyModel.get_categories(rights)
        print(result)
        return result.reverse()
    except Exception as e:
        print(f"Error in function 'utils.get_news_categories': {e}")
        return False

def get_post(newsletter_id, number_flag = True):
    try:
        result = MyModel.objects.get(id=newsletter_id)
        if number_flag:
            if result.data != '' and result.data != 'None' :
                result.data = len(result.data.split("|||"))
            else:
                result.data = 0
        return result

    except Exception as e:
        print(f"Error in function 'utils.get_post': {e}")
        return False


def get_posts_id(partial_chat_id):
    try:
        return MyModel.objects.filter(chat_id__icontains=partial_chat_id).values('chat_id', 'views')
    except Exception as e:
        print(f"Error in function 'utils.get_post': {e}")
        return False

#######################################################################################################################
