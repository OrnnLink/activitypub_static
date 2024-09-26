from datetime import datetime, timezone 
from modules.utility import extract_followers_inbox, get_follower_url, ActivityDTO
from modules.actor_info_retriever import *
from modules.activity_template import * 

class ActivityGenerator: 
    instance = None
    def get_instance():
        if ActivityGenerator.instance == None: 
            ActivityGenerator.instance = ActivityGenerator()
        return ActivityGenerator.instance
    
    def generate_follow_activity(self, actor_id, webfinger):
        template = FollowActivityTemplate(actor_id)
        return template.create(webfinger)
        
    def generate_publish_activity(self, actor_id, post_id, content, public):
        template = PublishActivityTemplate(actor_id, post_id, content, public)
        return template.create()
