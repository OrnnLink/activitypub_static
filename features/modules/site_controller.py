import os 
import json
import requests
from datetime import datetime, timezone, timedelta
from activity_template import PublishActivityTemplate
import sys

class SiteController:
    def __init__(self): 
        self.__load_config()

    def __load_config(self):
        filename = "config.json"
        with open(filename, "r") as fd:
            data = json.load(fd)
        self.username = data['username']
        self.domain = data['domain']
        self.actor_id = f"https://{self.domain}/{self.username}/user-info/actor.json"
        self.site_dir_path = data['site_dir_path']
        self.static_dir_path = data['site_dir_path'] + "/static"

    def add_follower(self, actor_id=None, webfinger=None): 
        if actor_id == None and webfinger == None:
            return
        if actor_id == None:
            actor_id = self.__add_user_with_webfinger(webfinger) 
            if actor_id == None:
                return
        handler = FileDataHandler(self.username, "Followers", self.static_dir_path)
        handler.update(actor_id)
    
    def add_following(self, actor_id=None, webfinger=None):
        if actor_id == None and webfinger == None:
            return
        if actor_id == None:
            actor_id = self.__add_user_with_webfinger(webfinger) 
            if actor_id == None:
                return
        handler = FileDataHandler(self.username, "Following", self.static_dir_path)
        handler.update(actor_id)
    
    def publish_post(self, url: str, title: str, content: str, public: bool=True):
        self.__write_publish_content(url, title, content)
        self.__add_content_to_outbox(url, title, content, public)

    def __add_user_with_webfinger(self, webfinger): 
        username, domain = webfinger.split("@")[1:]
        url = f"https://{domain}/.well-known/webfinger"
        params = { 
            "resource": f"acct:{username}@{domain}"
        }
        response = requests.get(url, params=params)
        if response.ok:
            data = json.loads(response.text)
            actor_id  = ""
            for value in data['links']:
                if value['rel'] == 'self':
                    actor_id = value['href']
                    break
            return actor_id
        return None

    def __write_publish_content(self, url, title, content):
        front_matter = self.__get_front_matter(title)
        file_content = f"{front_matter}" + f"# {title}\n" + f"{content}\n"
        dirname = self.__create_publish_folder(url)
        title = title.replace(" ", "_")
        filename = f"{dirname}/{title}.md"
        with open(filename, "w") as fd:
            fd.write(file_content)
        return dirname

    def __get_front_matter(self, title):
        front_matter ="+++\n"
        front_matter += f"title = '{title}'\n"
        front_matter += f"date = '{self.__get_current_time()}'\n"
        front_matter +="+++\n"
        return front_matter

    def __get_current_time(self):
        offset = timezone(timedelta(hours=10))
        current_time = datetime.now(offset).isoformat(timespec='seconds')
        return current_time
    
    def __create_publish_folder(self, url):
        dirs = url.split("/")
        dirname = self.site_dir_path + f"/content/{self.username}"
        for name in dirs:
            dirname += f"/{name}"
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
        return dirname

    def __create_static_publish_folder(self, url):
        dirs = url.split("/")
        dirname = f"{self.static_dir_path}/{self.username}/content"
        for name in dirs:
            dirname += f"/{name}"
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
        return dirname

    def __add_content_to_outbox(self, url, title, content, public):
        dirname = self.__create_static_publish_folder(url)
        follower_url = self.actor_id.replace("actor.json", "followers.json")
        post_id = f"https://{self.domain}/page/{self.username}/{url}/{title}"

        templator = PublishActivityTemplate(self.actor_id, post_id, content, public)
        data = templator.create_json_activity(None)
        self.__add_content_to_static_content(f"{dirname}/{title}.json", data)
        handler = FileDataHandler(self.username, "outbox", self.static_dir_path)
        handler.update(data)

    def __add_content_to_static_content(self, post_id, data):
        with open(post_id, "w") as fd:
            json.dump(data, fd, indent=4)

class FileDataHandler:
    def __init__(self, username, part_name, static_dir_path):
        self.username = username
        self.part_name = part_name
        self.static_dir_path = static_dir_path
    
    def update(self, data): 
        already_exists = self.__update_first_json(data)
        if not already_exists:
            self.__update_part_name_count()
            return True
        return False

    def __update_first_json(self, data):
        filename = f"{self.static_dir_path}/{self.username}/user-info/{self.part_name}/first.json"
        followers_json = self.read_json_from_file(filename)
        already_exists = True
        if not data in followers_json['orderedItems']:
            followers_json['orderedItems'].append(data)
            already_exists = False
            self.write_json_to_file(filename, followers_json)
        return already_exists
        
    def __update_part_name_count(self):
        filename = f"{self.static_dir_path}/{self.username}/user-info/{self.part_name}.json"
        followers_json = self.read_json_from_file(filename)
        followers_json['totalItems'] += 1
        self.write_json_to_file(filename, followers_json)
    
    def read_json_from_file(self, filename):
        with open(filename, "r") as fd:
            return json.load(fd)

    def write_json_to_file(self, filename, data):
        with open(filename, "w") as fd:
            json.dump(data, fd, indent=1)
         
c = SiteController()
url = "statuses"
content = "<p>Spring is coming</p>" 
title = "spring"
public = True
c.publish_post(url, title,content, public)

# def main():
#     c = SiteController()
#     args = sys.argv
#     if len(args) <= 1:
#         return
#     command = args[1]
#     if command == "follows":
#         data_type = args[2] 
#         if data_type == "webfinger":
#             c.add_follower(webfinger=args[3])
#         else:
#             c.add_follower(actor_id=args[3])


# if __name__ == "__main__":
#     main()
   

