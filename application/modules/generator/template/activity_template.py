from modules.utility import extract_username_and_domain, extract_followers_inbox
from modules.dto.activity_dto import ActivityDTO
from modules.retriever.actor_id_retriever import ActorIdRetriever
from modules.retriever.actor_inbox_retriever import ActorInboxRetriever

class ActivityTemplate:
    def __init__(self, actor_id, follower_url=None):
        self.actor_id = actor_id
        self.follower_url = follower_url
        self.__init_info_retriever()
    
    def set_webfinger(self, webfinger=None):
        self.webfinger = webfinger
        
    def create(self):
        base = self.__get_base_activity()
        base.activity = self.create_json_activity(base)
        base.followers = extract_followers_inbox(self.follower_url)
        return base

    def create_json_activity(self, base):
        return {}
    
    def __init_info_retriever(self):
        self.retriever = ActorIdRetriever()
        self.retriever.set_next(ActorInboxRetriever())

    def __get_base_activity(self):
        if self.webfinger == None: 
            return ActivityDTO()
        
        username, domain = extract_username_and_domain(self.webfinger)
        target_info = self.retriever.get_info([username, domain])
        if len(target_info) != 2:
            return target_info

        actor_id, inbox_url = target_info
        return ActivityDTO(
            domain=domain, actor_id=actor_id, inbox_url=inbox_url
        )
    

        