from datetime import datetime, timezone
from modules.generator.template.activity_template import ActivityTemplate

class PublishActivityTemplate(ActivityTemplate):
    def create_json_activity(self, base, data={}):
        date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Create",
            "id": data['post_id'],
            "actor": self.actor_id,
            "object": {
                "id": data['post_id'],
                "type": "Note", 
                "published": date,
                "content": data['content'],
                "attributedTo": self.actor_id,
                "to": [ self.follower_url],
                "cc": [ self.follower_url]
            },
            "to": [ self.follower_url],
            "cc": [ self.follower_url]
        }
        if data['public']:
            public_flag = "https://www.w3.org/ns/activitystreams#Public"
            activity["object"]['to'].append(public_flag)
            activity['to'].append(public_flag)
        return activity