from modules.utility import read_from_json
from modules.handler.activity_handler import ActivityHandler
from modules.handler.resource_handler import ResourceHandler
from modules.handler.webfinger_handler import WebfingerHandler
from modules.handler.user_data_handler import UserDataHandler

class ActivityController:
    def __init__(self):
        self.handler = {
            "activity": ActivityHandler(),
            "resource": ResourceHandler(),
            "webfinger": WebfingerHandler(),
            "user": UserDataHandler()
        }

    def send_follow_activity(self):
        data = read_from_json("activities/following_activity.json")
        webfinger = data['webfinger']
        if webfinger == "":
            return False

        resource_handler = self.handler['resource']
        if not resource_handler.add_following(webfinger):
            return False

        if self.handler['user'].add_following(webfinger=webfinger) is None:
            return False
        response = self.handler['activity'].send_follow_activity(webfinger)

    def send_unfollow_activity(self):
        data = read_from_json("activities/unfollow_activity.json")
        webfinger= data['webfinger']
        if webfinger == "":
            return False

        resource_handler = self.handler['resource']
        if not resource_handler.remove_following(webfinger):
            return False

        self.handler['user'].remove_following(webfinger=webfinger)
        response = self.handler['activity'].send_unfollow_activity(webfinger)

    def create_user(self):
        data = read_from_json("activities/webfinger_activity.json")
        username = data['username']
        if username == "":
            return False

        resource_handler = self.handler['resource']
        if not resource_handler.create_user_directory(username):
            self.handler['webfinger'].make_webfinger(username)
            return False
        self.handler['webfinger'].create_user(username)
        return True

    def update_followers(self):
        data = read_from_json("activities/update_followers_activity.json")
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

    def publish_content(self):
        data = read_from_json("activities/publish_activity.json")
        page_url, title, content, public = data.values()
        if title == "" or content == "":
            return False
        elif page_url == "":
            page_url = "page"

        resource_handler = self.handler['resource']
        domain = self.handler['activity'].domain
        username = self.handler['activity'].username
        post_id = f"https://{domain}/page/{username}/{page_url}/{title}"
        update = False
        if not resource_handler.add_post(post_id):
            update= True

        self.handler['user'].publish_post(page_url, title, content, public, update)
        responses = self.handler['activity'].send_publish_activity(post_id, content, public)

    def get_replies(self):
        # how would I solve this problem lmao 
        # Normally, people would send only one of them directly

        ...
