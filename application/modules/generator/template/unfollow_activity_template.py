from modules.generator.template.activity_template import ActivityTemplate

class UnFollowActivityTemplate(ActivityTemplate):
    def create_json_activity(self, activity_dto):
        activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Undo",
            "object": {
                "type": "Follow",
                "actor": self.actor_id,
                "object": activity_dto.target_id
            }
        }
        return activity
    