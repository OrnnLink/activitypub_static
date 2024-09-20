import requests 
import json

class ActorInfoRetriever:
    def __init__(self, next=None):
        self.next = next
    
    def set_next(self, next): 
        self.next = next

    def get_info(self, info):
        value = self.retrieve(info) 
        return value + self.__get_next(value[-1])

    def retrieve(self, info):
        return []

    def __get_next(self, info ):
        if self.next == None: 
            return [] 
        return self.next.get_info(info)

    def send_get_request(self, url, headers={}, params={}): 
        if headers == {}:
            headers = { "accept": "application/activity+json" }

        return requests.get(url, headers=headers, params=params)
    
class ActorObjectInfoRetriever(ActorInfoRetriever):
    def retrieve(self, info):
        username, domain = info
        url = f'https://{domain}/.well-known/webfinger'
        params = { "resource": f"acct:{username}@{domain}"}
        response = self.send_get_request(url, params=params)
        
        if not response.ok:
            return [ f"Unable to retrieve actor object: {response.reason}"]
        
        data = json.loads(response.text)
        links = data['links']
        for link in links:
            if link['rel'] == "self":
                return [ link['href']]
        
class ActorInboxInfoRetriever(ActorInfoRetriever):
    def retrieve(self, info):
        try: 
            response = self.send_get_request(info)
        except Exception:
            return [ f"Unknown actor object"]
            
        if not response.ok:
            return [ f"Unable to retrieve inbox: {response.reason}"]
    
        data = json.loads(response.text)
        inbox = data['inbox']
        inbox_endpoint = inbox.split("/")[3:]
        return [ inbox, "/" + "/".join(inbox_endpoint)]
