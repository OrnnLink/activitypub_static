import json
from datetime import datetime, timedelta, timezone

from modules.utility import make_directory, send_get_request
from modules.dto.activity_dto import ActivityDTO
from modules.handler.config_data_handler import ConfigDataHandler
from modules.handler.file_data_handler import FileDataHandler

from modules.generator.template.publish_activity_template import PublishActivityTemplate
from modules.generator.template.reply_activity_template import ReplyActivityTemplate

class UserDataHandler:
    def __init__(self):
        self.config_handler = ConfigDataHandler.get_instance()

    def add_follower(self, actor_id=None, webfinger=None):
        if actor_id == None and webfinger == None:
            return
        if actor_id == None:
            actor_id = self.__add_user_with_webfinger(webfinger)
            if actor_id == None:
                return
        handler = FileDataHandler(self.config_handler.username, "Followers", self.config_handler.static_dir_path)
        return handler.add_update(actor_id)

    def remove_follower(self, actor_id=None, webfinger=None):
        if actor_id == None and webfinger == None:
            return
        if actor_id == None:
            actor_id = self.__add_user_with_webfinger(webfinger)
            if actor_id == None:
                return
        handler = FileDataHandler(self.config_handler.username, "Followers", self.config_handler.static_dir_path)
        return handler.remove_update(actor_id)

    def add_following(self, actor_id=None, webfinger=None):
        if actor_id == None and webfinger == None:
            return
        if actor_id == None:
            actor_id = self.__add_user_with_webfinger(webfinger)
            if actor_id == None:
                return
        handler = FileDataHandler(self.config_handler.username, "Following", self.config_handler.static_dir_path)
        return handler.add_update(actor_id)

    def remove_following(self, actor_id=None, webfinger=None):
        if actor_id == None and webfinger == None:
            return
        if actor_id == None:
            actor_id = self.__add_user_with_webfinger(webfinger)
            if actor_id == None:
                return
        handler = FileDataHandler(self.config_handler.username, "Following", self.config_handler.static_dir_path)
        return handler.remove_update(actor_id)

    def publish_post(self, url: str, title: str, content: str, public: bool=True, update=False):
        self.__write_publish_content(url, title, content)
        self.__add_content_to_outbox(url, title.replace(' ', '_'), content, public, update)

    def add_reply(self, title: str, in_reply_to_id: int, content: str):
        self.__add_reply_to_outbox(title, in_reply_to_id, content)

    def __add_user_with_webfinger(self, webfinger):
        username, domain = webfinger.split("@")[1:]
        url = f"https://{domain}/.well-known/webfinger"
        params = {
            "resource": f"acct:{username}@{domain}"
        }
        response = send_get_request(url, params=params)
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
        file_content = f"{front_matter}" + f"{content}\n"
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
        dirname = self.config_handler.site_dir_path + f"/content/{self.config_handler.username}"
        for name in dirs:
            dirname += f"/{name}"
            make_directory(dirname)
        return dirname

    def __create_static_publish_folder(self, url):
        dirs = url.split("/")
        dirname = f"{self.config_handler.static_dir_path}/{self.config_handler.username}/content"
        for name in dirs:
            dirname += f"/{name}"
            make_directory(dirname)
        return dirname

    def __add_content_to_outbox(self, url, title, content, public, update=True):
        dirname = self.__create_static_publish_folder(url)
        post_id = f"https://{self.config_handler.domain}/page/{self.config_handler.username}/{url}/{title}"
        templator = PublishActivityTemplate(
            self.config_handler.actor_id
        )
        data = templator.create_json_activity(
         ActivityDTO(
                username=self.config_handler.username, post_id=post_id, content=content, public=public,
                follower_url=self.config_handler.actor_id.replace("actor.json", "followers.json")
            )
        )
        self.__add_content_to_static_content(f"{dirname}/{title.replace(' ', '_')}.json", data)
        handler = FileDataHandler(self.config_handler.username, "outbox", self.config_handler.static_dir_path)
        handler.add_update(data, not update)

    def __add_reply_to_outbox(self, title, in_reply_to_id, content):
        post_id = f"https://{self.config_handler.domain}/{self.config_handler.username}/replies/{title}"
        templator = ReplyActivityTemplate(self.config_handler.actor_id)
        data = templator.create_json_activity(
            ActivityDTO(
                post_id=post_id, in_reply_to_id=in_reply_to_id, content=content
            )
        )
        dirname = f'{self.config_handler.static_dir_path}/{self.config_handler.username}/replies'
        self.__add_content_to_static_content(f"{dirname}/{title.replace(' ', '_')}.json", data)
        # handler = FileDataHandler(self.username, "outbox", self.static_dir_path)
        # handler.add_update(data, not update)

    def __add_content_to_static_content(self, post_id, data):
        with open(post_id, "w") as fd:
            json.dump(data, fd, indent=4)
