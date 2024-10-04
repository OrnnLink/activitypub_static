from modules.utility import read_from_json
class ConfigDataHandler:
    instance = None
    
    # Singleton
    def get_instance():
        if ConfigDataHandler.instance == None:
            ConfigDataHandler.instance = ConfigDataHandler()
        return ConfigDataHandler.instance


    def __init__(self, filename: str=None):
        self.filename = "config.json"
        if filename != None:
            self.filename = self.filename
        self.__load_config()
        
    def __load_config(self):
        filename = "config.json"
        data = read_from_json(filename)

        self.username = data['username']
        self.domain= data['domain']
        self.site_dir_path = data["site_dir_path"]
        self.static_dir_path = f"{self.site_dir_path}/static"
        self.public_key_path = data["public_key_path"]
        self.actor_id = f"https://{self.domain}/{self.username}/user-info/actor.json"
        self.follower_url = f"https://{self.domain}/{self.username}/user-info/followers.json"
        self.following_url = f"https://{self.domain}/{self.username}/user-info/following.json"
        self.private_key_path = data["private_key_path"]