from modules.utility import read_from_json, write_to_json, make_directory
from modules.handler.config_data_handler import ConfigDataHandler

class ResourceHandler:
    def __init__(self, path="resources/users"):
        self.path = path 
        self.__setup()
    
    def __setup(self):
        self.config_handler = ConfigDataHandler.get_instance()
        path = f"{self.path}/{self.config_handler.username}"
        self.create_user_directory(self.config_handler.username)
        self.followers = read_from_json(f"{path}/followers.json") 
        self.following = read_from_json(f"{path}/following.json") 
        self.posts = read_from_json(f"{path}/posts.json") 
        self.replies = read_from_json(f"{path}/replies.json")
    
    def update_config(self, data: dict):
        config_data = read_from_json(self.config_handler.filename)
        for key in data:
            config_data[key] = data[key]
        write_to_json(config_data, self.config_handler.filename)
    
    def create_user_directory(self, username, domain=""):
        path = f"{self.path}/{username}"
        config_update = {"username": username}
        if domain != "":
            self.domain = domain
            config_update['domain'] = domain

        self.update_config(config_update)
        if not make_directory(path):
            return False 
        write_to_json({"webfingers": []}, f"{path}/followers.json")
        write_to_json({"webfingers": []}, f"{path}/following.json")
        write_to_json({"posts": []}, f"{path}/posts.json")
        write_to_json({"posts": [], "reply_count": 0}, f"{path}/replies.json")
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
        path = f"{self.path}/{self.config_handler.username}"
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
        path = f"{self.path}/{self.config_handler.username}"
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
        path = f"{self.path}/{self.config_handler.username}"
        make_directory(path)
        path += '/posts.json'
        write_to_json(data, path)

    # Reply Data
    def add_reply(self, in_reply_to_id, content):
        count = self.replies['reply_count']
        self.replies['posts'].append({
            "id": count,
            "in_reply_to_id": in_reply_to_id,
            "content": content
        })
        self.replies['reply_count'] = count + 1
        self.update_user_reply_list(self.replies)
        return count+1

    def update_user_reply_list(self, data: list):
        path = f"{self.path}/{self.config_handler.username}"
        make_directory(path)
        path += "/replies.json"
        write_to_json(data, path)

