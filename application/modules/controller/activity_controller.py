from modules.utility import read_from_json
from modules.handler.activity_handler import ActivityHandler
from modules.handler.resource_handler import ResourceHandler
from modules.handler.webfinger_handler import WebfingerHandler 

class ActivityController:
    def __init__(self):
        self.handler = {
            "activity": ActivityHandler(),
            "resource": ResourceHandler(),
            "webfinger": WebfingerHandler()
        }
    
    def send_follow_activity(self, webfinger: str):
        resource_handler = self.handler['resource']
        if not resource_handler.add_follower(webfinger):
            return False
        self.handler['activity'].send_follow_activity(webfinger)
        return True
    
    def create_user(self):
        data = read_from_json("activities/webfinger_activity.json")
        username = data['username']
        if username == "":
            return False 

        resource_handler = self.handler['resource']
        if not resource_handler.create_user_directory(username):
            return False 
        self.handler['webfinger'].create_user(username)
        return True
    
    
    