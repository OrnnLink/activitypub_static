from datetime import datetime, timezone 
from modules.utility import extract_followers_inbox, get_follower_url, ActivityDTO
from modules.actor_info_retriever import *

class ActivityGenerator: 
    instance = None
    def get_instance():
        if ActivityGenerator.instance == None: 
            ActivityGenerator.instance = ActivityGenerator()
        return ActivityGenerator.instance
    
    def generate_follow_activity(self, actor_id, webfinger):
        template = FollowActivityTemplate(actor_id)
        return template.create(webfinger)
        
    # def generate_accept_activity(self, actor_id, webfinger):
    #     template = AcceptActivityTemplate(actor_id)
    #     return template.create(webfinger)
      
    def generate_publish_activity(self, actor_id, post_id, content, public):
        template = PublishActivityTemplate(actor_id, post_id, content, public)
        return template.create()

    # def generate_delete_activity(self, actor_id, post_id):
    #     template = DeleteActivityTemplate(actor_id, post_id)
    #     return template.create()

class ActivityTemplate:
    def __init__(self, actor_id, follower_url=None):
        self.actor_id = actor_id
        self.follower_url = follower_url 
        self.__init_info_retriever()

    def create(self, webfinger=None):
        base = self.__get_base_activity(webfinger)
        if isinstance(base, list): 
            return base
        base.activity = self.create_json_activity(base)
        self.extract_followers_inbox(base)
        return base
    
    def __get_base_activity(self, webfinger):
        if webfinger == None:
            return ActivityDTO()

        username, domain = webfinger.split("@")[1:]
        # Retrieve information from webfinger
        values = self.__get_webfinger_info(username, domain)
        if len(values) != 3:
            return values
        target_actor_id, inbox_url, inbox_endpoint = values
        return ActivityDTO(domain, target_actor_id, inbox_url, inbox_endpoint)

    def __init_info_retriever(self):
        self.retriever = ActorObjectInfoRetriever()
        self.retriever.set_next( ActorInboxInfoRetriever()) 

    def __get_webfinger_info(self, username, domain):
        return self.retriever.get_info([username, domain])

    def create_json_activity(self, base):
        return {}
    
    def extract_followers_inbox(self, base):
        if self.follower_url == None:
            return
        extract_followers_inbox(self.follower_url, base)

class FollowActivityTemplate(ActivityTemplate):
    def __init__(self, actor_id):
        super().__init__(actor_id=actor_id)
    
    def create_json_activity(self, base):
        activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Follow",
            "actor": self.actor_id,
            "object": base.target_actor_id
        }
        return activity

# class AcceptActivityTemplate(ActivityTemplate):
#     def __init__(self, actor_id):
#         super().__init__(actor_id=actor_id)
    
#     def create_json_activity(self, base):
#         activity = {
#             "@context": "https://www.w3.org/ns/activitystreams",
#             "type": "Accept",
#             "actor": self.actor_id,
#             "object": { 
#                "@context": "https://www.w3.org/ns/activitystreams",
#                 "type": "Follow",
#                 "actor": base.target_actor_id,
#                 "object": self.actor_id,
#             }
#         }
#         return activity

class PublishActivityTemplate(ActivityTemplate):
    def __init__(self, actor_id, post_id, content, public):
        self.post_id = post_id
        self.content = content
        self.public = public
        super().__init__(actor_id, get_follower_url(actor_id))
        
    def create_json_activity(self, base):
        date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Create",
            "id": self.post_id,
            "actor": self.actor_id,
            "object": {
                "id": self.post_id,
                "type": "Note", 
                "published": date,
                "content": self.content,
                "attributedTo": self.actor_id,
                "to": [ self.follower_url],
                "cc": [ self.follower_url]
            },
            "to": [ self.follower_url],
            "cc": [ self.follower_url]
        }
        if self.public:
            public_flag = "https://www.w3.org/ns/activitystreams#Public"
            activity["object"]['to'].append(public_flag)
            activity['to'].append(public_flag)
        return activity

# class DeleteActivityTemplate(ActivityTemplate):
#     def __init__(self, actor_id, post_id):
#         self.post_id = post_id
#         super().__init__(actor_id, get_follower_url(actor_id))
        
#     def create_json_activity(self, base):
#         activity = {
#             "@context": "https://www.w3.org/ns/activitystreams",
#             "type": "Delete",
#             "actor": self.actor_id,
#             "object": self.post_id
#         }
#         return activity
