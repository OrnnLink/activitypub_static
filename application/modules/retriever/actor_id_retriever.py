import json
from modules.utility import send_get_request
from modules.retriever.info_retriever import InfoRetriever

class ActorIdRetriever(InfoRetriever):
    def retrieve(self, data):
        username, domain = data
        url = f"https://{domain}/.well-known/webfinger"
        params = { 
            "resource": f"acct:{username}@{domain}"
        }
        response = send_get_request(url, params=params)
        data = json.loads(response.text)
        links = data['links']
        for link in links:
            if link['rel'] == "self":
                self.value = [ link['href']]
                return link['href']


