from modules.handler.base_handler import BaseHandler

class ActivityHandler(BaseHandler): 
    def send_follow_activity(self, webfinger):
        ...

    def send_publish_activity(self, post_id, content, public=True):
        ...
