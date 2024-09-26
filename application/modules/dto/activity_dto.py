class ActivityDTO:
    def __init__(self, domain="", actor_id="", inbox_url ="", activity=""):
        self.domain = domain
        self.actor_id = actor_id
        self.inbox_url = inbox_url
        self.activity = activity
    
    def get_inbox_endpoint(self):
        inbox_endpoint = self.inbox_url.split("/")[3:]
        return "/" + "/".join(inbox_endpoint)

    def __str__(self): 
        line = f"Domain: {self.domain}\n"
        line += f"Actor ID: {self.actor_id}\n"
        line += f"Inbox URL: {self.inbox_url}\tEndpoint: {self.get_inbox_endpoint()}\n"
        line += f"Activity: {self.activity}\n"
        return line