import requests
import json

class ActivityDTO:
    def __init__(self, 
        domain="", target_actor_id="",
        inbox_url="", inbox_endpoint="",
        activity=""
    ):
        self.domain = domain
        self.target_actor_id = target_actor_id
        self.inbox_url = inbox_url
        self.inbox_endpoint = inbox_endpoint
        self.activity = activity

def get_follower_url(actor_id): 
    response = requests.get(actor_id, headers={ "accept": "application/activity+json"})
    data = json.loads(response.text)
    return data['followers']

def extract_followers_inbox(follower_url, activity_dto):
    follower_ids = __get_followers_id(follower_url)
    __add_inbox_to_url(follower_ids)
    followers = []
    for follower_id in follower_ids:
        domain= follower_id.split("/")[2]
        # Getting inbox endpoint
        inbox_endpoint = follower_id.split("/")[3:]
        inbox_endpoint = "/" + "/".join(inbox_endpoint)
        followers.append([domain, follower_id, inbox_endpoint])
    activity_dto.followers = followers

def extract_followers_outbox(follower_url, activity_dto):
    our_domain = "sdlay.netlify.app"
    follower_ids = __get_followers_id(follower_url)
    __add_outbox_to_url(follower_ids)
    followers = []
    for follower_id in follower_ids:
        domain= follower_id.split("/")[2]
        if our_domain == domain:
            follower_id = f"https://{domain}/user-info/ylay/outbox.json"
        outbox_endpoint = follower_id.split("/")[3:]
        outbox_endpoint = "/" + "/".join(outbox_endpoint)
        followers.append([domain, follower_id, outbox_endpoint])
    activity_dto.followers = followers
    
def __add_inbox_to_url(follower_ids):
    for i, follower_id in enumerate(follower_ids):
        if "inbox" not in follower_id:
            if "/" != follower_id[-1]:
                follower_id += "/"
            follower_id += "inbox"
            follower_ids[i] = follower_id

def __add_outbox_to_url(follower_ids):
    for i, follower_id in enumerate(follower_ids):
        if "outbox" not in follower_id:
            if "/" != follower_id[-1]:
                follower_id += "/"
            follower_id += "outbox"
            follower_ids[i] = follower_id

def __get_followers_id(follower_url):
    response = requests.get(follower_url, headers={ "accept": "application/activity+json"})     
    data = json.loads(response.text)
    
    if "orderedItems" in data:
        return __get_follower_from_ordered_items(data)
    return __get_follower_from_ext_urls(data)

def __get_follower_from_ordered_items( data): 
        items = data['orderedItems']
        follower_ids = []
        for item in items: 
            if type(item) == str:
                follower_ids.append(item)
            elif type(item) == dict: 
                follower_ids.append(item['id'])
        return items
        
def __get_follower_from_ext_urls(data):
    excluded_keys = [ "@context", "id", "type", "totalItems"] 
    urls = []
    # Getting relevant urls
    for key in data:
        if key not in excluded_keys:
            urls.append(data[key])
    
    total = None
    follower_ids = [] 
    while True:
        url = urls.pop(0)
        response = requests.get(url, headers={ "accept": "application/activity+json"})
        json_data = json.loads(response.text)
        
        # Registers total Items
        if total == None: 
            total = json_data['totalItems']
            
        if "orderedItems" not in json_data.keys(): 
            break 
        
        for item in json_data['orderedItems']:
            if type(item) == str:
                follower_ids.append(item)
            elif type(item) == dict: 
                follower_ids.append(item['id'])
        
        if len(follower_ids) >= total: 
            break

        # Registered the next urls
        if "next" in json_data.keys():
            urls.append(json_data["next"])
        elif "last" in json_data.keys():
            urls.append(json_data["last"])
        else: 
            break
    return follower_ids


 