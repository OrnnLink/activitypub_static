class ActivityDTO:
    def __init__(self,
            domain="", username="", actor_id="", 
            follower_url="", inbox_url ="", outbox_url="",
            post_id="", target_id="", in_reply_to_id="",
            activity="",
            content="", 
            webfinger=None, 
            public=False
        ):
        self.domain = domain
        self.username = username
        self.actor_id = actor_id

        self.follower_url = follower_url
        self.inbox_url = inbox_url
        self.outbox_url = outbox_url

        self.target_id = target_id
        self.post_id = post_id 
        self.in_reply_to_id = in_reply_to_id

        self.content = content
        self.activity = activity
        self.webfinger = webfinger
        self.public = public

    def get_inbox_endpoint(self):
        inbox_endpoint = self.inbox_url.split("/")[3:]
        return "/" + "/".join(inbox_endpoint)

    def get_outbox_endpoint(self):
        outbox_endpoint = self.outbox_url.split("/")[3:]
        return "/" + "/".join(outbox_endpoint)

    def __str__(self): 
        line = f"Domain: {self.domain}\n"
        line += f"Actor ID: {self.actor_id}\n"
        line += f"Inbox URL: {self.inbox_url}\tEndpoint: {self.get_inbox_endpoint()}\n"
        line += f"Activity: {self.activity}\n"
        return line