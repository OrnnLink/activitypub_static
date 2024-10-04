from modules.utility import read_from_json, write_to_json
from modules.handler.activity_handler import ActivityHandler
from modules.handler.resource_handler import ResourceHandler
from modules.handler.webfinger_handler import WebfingerHandler
from modules.handler.user_data_handler import UserDataHandler
from modules.handler.get_reply_handler  import GetReplyHandler

class ActivityController:
    def __init__(self):
        self.handler = {
            "activity": ActivityHandler(),
            "resource": ResourceHandler(),
            "webfinger": WebfingerHandler(),
            "user": UserDataHandler(),
            "reply": GetReplyHandler()
        }

    def send_follow_activity(self):
        filename = "activities/following_activity.json"
        data = read_from_json(filename)
        webfinger = data['webfinger']
        if webfinger == "":
            return False

        resource_handler = self.handler['resource']
        if not resource_handler.add_following(webfinger):
            return False

        if self.handler['user'].add_following(webfinger=webfinger) is None:
            return False
        response = self.handler['activity'].send_follow_activity(webfinger)
        data = { "webfinger": ""}
        self.__reset_activity(data, filename)


    def send_unfollow_activity(self):
        filename = "activities/unfollow_activity.json"
        data = read_from_json(filename)
        webfinger= data['webfinger']
        if webfinger == "":
            return False

        resource_handler = self.handler['resource']
        if not resource_handler.remove_following(webfinger):
            return False

        self.handler['user'].remove_following(webfinger=webfinger)
        response = self.handler['activity'].send_unfollow_activity(webfinger)
        data = { "webfinger": ""}
        self.__reset_activity(data, filename)

    def create_user(self):
        data = read_from_json("activities/webfinger_activity.json")
        username, domain = data.values()
        if username == "" and domain == "":
            return False

        resource_handler = self.handler['resource']
        if not resource_handler.create_user_directory(username, domain):
            self.handler['webfinger'].domain = domain
            self.handler['webfinger'].make_webfinger(username)
            self.handler['webfinger'].make_actor_object(username)
            return False
        self.handler['webfinger'].create_user(username, domain)
        return True

    def update_followers(self):
        filename = "activities/update_followers_activity.json"
        data = read_from_json(filename)
        webfinger = data['webfinger']
        add_followers = data['add_follower']
        if webfinger == "":
            return False

        resource_handler = self.handler['resource']
        if add_followers:
            self.handler['user'].add_follower(webfinger=webfinger)
            resource_handler.add_follower(webfinger)
            return

        self.handler['user'].remove_follower(webfinger=webfinger)
        resource_handler.remove_follower(webfinger)

        data = { "webfinger": "", "add_follower": True}
        self.__reset_activity(data, filename)


    def publish_content(self):
        filename = "activities/publish_activity.json"
        data = read_from_json(filename)
        page_url, title, content, public = data.values()
        if title == "" or content == "":
            return False
        elif page_url == "":
            page_url = "page"

        resource_handler = self.handler['resource']
        domain = self.handler['activity'].config_handler.domain
        username = self.handler['activity'].config_handler.username
        post_id = f"https://{domain}/page/{username}/{page_url}/{title.replace(' ', '_')}"
        update = False
        if not resource_handler.add_post(post_id):
            update= True


        self.handler['user'].publish_post(page_url, title, content, public, update)
        responses = self.handler['activity'].send_publish_activity(post_id, content, public)

        data = { "page_url": "statuses", "title": "", "content": "", "public": True}
        self.__reset_activity(data, filename)

    def get_replies(self):
        handler = self.handler['reply']
        replies = handler.get_replies()

        for reply in replies:
            handler.interpret_reply(reply)
        return replies

    def send_reply(self):
        filename = "activities/reply_to_post_activity.json"
        data = read_from_json(filename)
        in_reply_to_id, content = data.values()
        if in_reply_to_id == '' or content == '':
            return False
        in_reply_to_id = self.__format_in_reply_to_id(in_reply_to_id)

        resource_handler = self.handler['resource']
        count = resource_handler.add_reply(in_reply_to_id, content)-1
        self.handler['user'].add_reply(f"reply_{count}", in_reply_to_id, content)
        responses = self.handler['activity'].send_reply_activity(count, in_reply_to_id, content)
        data = { "in_reply_to_id": "", "content": ""}
        self.__reset_activity(data, filename)

    def __format_in_reply_to_id(self, in_reply_to_id):
        split_data = in_reply_to_id.split("/")
        i = len(split_data) - 1
        while i > 2:
            try:
                ele = int(split_data[i])
            except ValueError:
                split_data.pop(i)
                i -= 1
                continue
            break

        return "/".join(split_data)

    def __reset_activity(self, data, filename):
        write_to_json(data, filename)


        