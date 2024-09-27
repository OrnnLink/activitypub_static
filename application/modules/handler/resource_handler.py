from modules.utility import read_from_json, write_to_json, make_directory
from modules.handler.base_handler import BaseHandler

class ResourceHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.__setup()
    
    def __setup(self):
        path = f"resources/users/{self.username}"
        self.create_user_directory(self.username)
        self.followers = read_from_json(f"{path}/followers.json") 
        self.following = read_from_json(f"{path}/following.json") 
        self.posts = read_from_json(f"{path}/posts.json") 
    
    def update_config(self, data: dict):
        config_data = read_from_json("config.json")
        for key in data:
            config_data[key] = data[key]
        write_to_json(config_data, "config.json")
    
    def create_user_directory(self, username):
        path = f"resources/users/{username}"
        self.update_config({"username": username})
        if not make_directory(path):
            return False
        write_to_json({"webfingers": []}, f"{path}/followers.json")
        write_to_json({"webfingers": []}, f"{path}/following.json")
        write_to_json({"posts": []}, f"{path}/posts.json")
        return True
    
    # Followers Data
    def add_follower(self, follower_webfinger):
        if follower_webfinger in self.followers['webfingers']:
            return False
        self.followers['webfingers'].append(follower_webfinger)
        self.update_user_followers_list(self.followers)
        return True
    
    def remove_follower(self, follower_webfinger):
        if follower_webfinger not in self.followers['webfingers']:
            return False
        self.followers['webfingers'].remove(follower_webfinger)
        self.update_user_followers_list(self.followers)
        return True

    def update_user_followers_list(self, data: list):
        path = f"resources/users/{self.username}"
        make_directory(path)
        path += '/followers.json'
        write_to_json(data, path)
    
    # Following Data
    def add_following(self, webfinger):
        if webfinger in self.following['webfingers']:
            return False
        self.following['webfingers'].append(webfinger)
        self.update_user_following_list(self.following)
        return True
    
    def remove_following(self, webfinger):
        if webfinger not in self.following['webfingers']:
            return False
        self.following['webfingers'].remove(webfinger)
        self.update_user_following_list(self.following)
        return True
        
    def update_user_following_list(self, data: list):
        path = f"resources/users/{self.username}"
        make_directory(path)
        path += '/following.json'
        write_to_json(data, path)
    
    # Post Data
    def add_post(self, post_id):
        if post_id in self.posts['posts']:
            return False
        self.posts['posts'].append(post_id)
        self.update_user_post_list(self.posts)
        return True

    def remove_post(self, post_id):
        if post_id not in self.posts['posts']:
            return False
        self.posts['posts'].remove(post_id)
        self.update_user_post_list(self.posts)
        return True
    
    def update_user_post_list(self, data: list):
        path = f"resources/users/{self.username}"
        make_directory(path)
        path += '/posts.json'
        write_to_json(data, path)