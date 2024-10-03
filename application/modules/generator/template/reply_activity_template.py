from datetime import datetime, timezone
from modules.generator.template.activity_template import ActivityTemplate

class ReplyActivityTemplate(ActivityTemplate):
    def create_json_activity(self, activity_dto):
        date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        post_id = activity_dto.post_id
        content = activity_dto.content
        reply_to_post_id = activity_dto.reply_to_post_id

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
                "inReplyTo":  reply_to_post_id
            },
        }
        return activity
    