from modules.generator.template.activity_template import ActivityTemplate

class FollowActivityTemplate(ActivityTemplate):
    def create_json_activity(self, base, data={}):
        activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Follow",
            "actor": self.actor_id,
            "object": base.actor_id 
        }
        return activity
    