from datetime import datetime, timezone
from modules.generator.template.activity_template import ActivityTemplate

class PublishActivityTemplate(ActivityTemplate):
    def create_json_activity(self, activity_dto):
        date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        post_id = activity_dto.post_id
        content = activity_dto.content
        public = activity_dto.public
        follower_url  = activity_dto.follower_url
        activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Create",
            "id": post_id,
            "actor": self.actor_id,
            "object": {
                "id": post_id,
                "type": "Note", 
                "published": date,
                "content": content,
                "attributedTo": self.actor_id,
                "to": [ follower_url],
                "cc": [ follower_url]
            },
            "to": [ follower_url],
            "cc": [ follower_url]
        }
        if public:
            public_flag = "https://www.w3.org/ns/activitystreams#Public"
            activity["object"]['to'].append(public_flag)
            activity['to'].append(public_flag)
        return activity
    