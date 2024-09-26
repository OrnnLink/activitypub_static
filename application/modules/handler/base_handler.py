import json

class BaseHandler:
    def __init__(self, filename: str=None):
        self.filename = "config.json"
        if filename != None:
            self.filename = self.filename
        self.__load_config()
        
    def __load_config(self):
        filename = "config.json"
        with open(filename, "r") as fd:
            data = json.load(fd)

        self.username = data['username']
        self.domain= data['domain']
        self.site_dir_path = data["site_dir_path"]
        self.public_key_path = data["public_key_path"]
        self.actor_id = f"https://{self.domain}/{self.username}/user-info/actor.json"
        self.follower_url = f"https://{self.domain}/{self.username}/user-info/followers.json"
        self.following_url = f"https://{self.domain}/{self.username}/user-info/following.json"
        self.private_key_path = data["private_key_path"]