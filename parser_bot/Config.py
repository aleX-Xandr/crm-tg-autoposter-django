#ALL CONFIG
import json
api_hash = "a7f5b1dbe83336753cbc8213e37ad6f1"
api_id   = 27835888
Token_bot = "6413913546:AAGrB_f8axg5yOIAqI6mljBSdQ_aL6jEWrU"
OWNER_ID = 6864232030
ADMINS = [OWNER_ID]
PROJECT = "first"
CHAT_ID = -1001660917160
TOPIC_CHAT_IDS = [-1002044596409, -1002141596554]
SERVER_URI = "http://127.0.0.1:8000/"
CHANNEL_LINK = '\n\n<a href="https://t.me/lvivskyi_djadko">Пiдписатися</a> | <a href="https://t.me/Djadko_bot">Поділитися новиною</a>'
def get_channels_info(channel="all"):
	if not type(channel) is str:
		channel = str(channel)
	with open('file.json', encoding='utf8') as f: 
		data = json.load(f) 
	if channel == "all":
		return data
	if channel in data:
		return data[channel]
	return None
def get_projects_info(project="all"):
	with open('../web/superpanel/projects.json', encoding='utf8') as f: 
		projects = json.load(f) 
	if project == "all":
		return projects
	for pr in projects:
		if pr["access"] == project:
			return pr
	return None