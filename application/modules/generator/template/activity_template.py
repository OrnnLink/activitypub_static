from modules.utility import extract_username_and_domain
from modules.retriever.actor_id_retriever import ActorIdRetriever

class ActivityTemplate:
    def __init__(self, actor_id):
        self.actor_id = actor_id
        self.retriever = ActorIdRetriever()
        
    def create(self, activity_dto):
        self.__get_base_activity(activity_dto)
        return self.create_json_activity(activity_dto)

    def create_json_activity(self, activity_dto):
        return {}
    
    def __get_base_activity(self, activity_dto):
        if activity_dto.webfinger is None:
            return 
        
        username, domain = extract_username_and_domain(activity_dto.webfinger)
        target_info = self.retriever.get_info([username, domain])
        if len(target_info) != 1:
            return
        activity_dto.target_id = target_info[0]

        

        