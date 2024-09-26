import json
from modules.utility import send_get_request
from modules.retriever.info_retriever import InfoRetriever

class ActorInboxRetriever(InfoRetriever):
    def retrieve(self, data): 
        response = send_get_request(data)
        data = json.loads(response.text)
        inbox = data['inbox']
        # inbox_endpoint = inbox.split("/")[3:]
        # self.value =[ inbox, "/" + "/".join(inbox_endpoint)]
        self.value = [inbox]
        return self.value

