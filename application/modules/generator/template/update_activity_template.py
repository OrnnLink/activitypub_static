from datetime import datetime, timezone
from modules.generator.template.activity_template import ActivityTemplate

class UpdateActivityTemplate(ActivityTemplate):
    def create_json_activity(self, activity_dto):
        date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        post_id = activity_dto.post_id
        content = activity_dto.content
        public = activity_dto.public
        follower_url  = activity_dto.follower_url
        activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Update",
            "actor": self.actor_id,
            "object": {
                "id": post_id.replace(f"page/{activity_dto.username}", f"{activity_dto.username}/content"),
                "type": "Note", 
                "content": content,
                "updated": date,
                "to": [ follower_url],
                "attributedTo": self.actor_id
            },
            "to": [ follower_url]
        }
        if public:
            public_flag = "https://www.w3.org/ns/activitystreams#Public"
            activity["object"]['to'].append(public_flag)
            activity['to'].append(public_flag)
        return activity
    