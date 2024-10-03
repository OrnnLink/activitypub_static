from modules.generator.template.follow_activity_template import FollowActivityTemplate
from modules.generator.template.unfollow_activity_template import UnFollowActivityTemplate
from modules.generator.template.publish_activity_template import PublishActivityTemplate
from modules.generator.template.update_activity_template import UpdateActivityTemplate

class ActivityGenerator:
    instance = None
    def get_instance():
        if ActivityGenerator.instance == None: 
            ActivityGenerator.instance = ActivityGenerator()
        return ActivityGenerator.instance
    
    def generate_follow_activity(self, actor_id, activity_dto):
        template = FollowActivityTemplate(actor_id)
        return template.create(activity_dto)
        
    def generate_publish_activity(self, actor_id, activity_dto):
        template = PublishActivityTemplate(actor_id)
        return template.create(activity_dto)
    
    def generate_unfollow_activity(self, actor_id, activity_dto):
        template = UnFollowActivityTemplate(actor_id)
        return template.create(activity_dto)

    def generate_update_activity(self, actor_id, activity_dto):
        template = UpdateActivityTemplate(actor_id)
        return template.create(activity_dto)

    def generate_reply_activity(self, actor_id, activity_dto): 
        template = UpdateActivityTemplate(actor_id)
        return template.create(activity_dto)
