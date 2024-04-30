from django.conf import settings
import json
from accounts.models import UserDatabase

def projects_data(request):
    try:
        projects_data = []
        username = request.COOKIES.get('username')
        if username:
            user = UserDatabase.get_record_by_login(username)
            if not user is None:
                
                with open('web/superpanel/projects.json', 'r') as json_file:
                    projects_file = json.load(json_file)
                    for project in projects_file:
                        if project["access"] in user.rights:
                            projects_data.append(project)
    except FileNotFoundError:
        pass
    
    return {'projects_data': projects_data}

def is_superadmin(request):
    print("CONTEXT PROCESSOR: ", (request.user.is_authenticated and request.user.username == "superadmin"))
    return {"is_superadmin": (request.user.is_authenticated and request.user.username == "superadmin")}
                                    
