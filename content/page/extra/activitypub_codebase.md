+++
title = 'ActivityPub Codebase'
date = 2024-08-09T16:09:39+10:00
draft = false
+++

We will be implementing a couple of handler objects for generating activity and sending out request to execute [ActivityPub Activity](https://www.w3.org/ns/activitystreams). The codebase will be implemented using Python, it is recommended that you install the following python libraries on your machine or python environment:

```bash
pip install cryptography
pip install requests
```

{{< callout type="note" title="Note" >}}
Different ActivityPub platforms require varying levels of security for signatures. The algorithm discussed in this section has been tested with Mastodon, Honk, and Ktistec. While it works successfully with Mastodon and Honk, Ktistec demands additional security measures that have not yet been fully addressed due to resource constraints.
{{< /callout >}}
+++
title = 'ActivityPub Codebase'
date = 2024-08-09T16:09:39+10:00
draft = false
+++

We will be implementing a couple of handler objects for generating activity and sending out request to execute [ActivityPub Activity](https://www.w3.org/ns/activitystreams). The codebase will be implemented using Python, it is recommended that you install the following python libraries on your machine or python environment:

```bash
pip install cryptography
pip install requests
```

{{< callout type="note" title="Note" >}}
Different ActivityPub platforms require varying levels of security for signatures. The algorithm discussed in this section has been tested with Mastodon, Honk, and Ktistec. While it works successfully with Mastodon and Honk, Ktistec demands additional security measures that have not yet been fully addressed due to resource constraints.
{{< /callout >}}

For quick navigation, you can use the following links:

1. [Usage]({{< relref "#usage" >}}) - Overview of how to use the codebase.
2. [Activity Handler]({{< relref "#activity_handler" >}}) - Details about the `ActivityHandler` class.
3. [Activity Generator]({{< relref "#activity_generator" >}}) - Details about the `ActivityGenerator` class.
4. [Activity Request]({{< relref "#activity_request" >}}) - Details about the `ActivityRequest` class.
5. [Actor Info Retriever]({{< relref "#actor_info_retriever" >}}) - Details about the `ActorInfoRetriever` class.
6. [Utility]({{< relref "#utility" >}}) - Contains common functions used by various classes.

The refactoring process involved converting the algorithm to a more object-oriented approach and separating the functionality into four components:

1. **`ActivityHandler (Facade)`** - The entry point of the algorithm, providing a simplified interface for sending various Activities.
2. **`ActivityGenerator (Singleton)`** - Responsible for generating ActivityPub activity JSON objects based on provided parameters. Currently supports `@Follow`, `@Create`, and `@Delete`.
3. **`ActivityRequest`** - Manages and organizes information to ensure the HTTP request structure is correct before sending.
4. **`ActorInfoRetriever (Chain of Responsibility)`** - A chain of information retrievers used to gather relevant data about a particular actor to complete a request. Currently includes:
   - **`ActorObjectInfoRetriever`** - Extracts the URL leading to the actor object given the username and domain.
   - **`ActorInboxInfoRetriever`** - Retrieves the inbox URL of a specific ActivityPub actor and extracts the endpoint from that URL.


## Using the Codebase {#usage}

To initialize the `ActivityHandler`, provide the constructor with the following parameters:
1. **`actor_id`** - The URL pointing to your actor object in JSON format.
2. **`private_key_path`** - The path to your private key file.

### Example: Follow Activity

```python
from activity_handler import ActivityHandler

actor_id = "https://noah.netlify.app/noah/actor.json"
private_key_path = "..."

webfinger = "@alice@mastodon.social"

handler = ActivityHandler(
    actor_id=actor_id, 
    private_key_path=private_key_path
)

handler.send_follow_activity(webfinger=webfinger)
```

### Example: Publish Activity

For publishing an activity, the `ActivityHandler` first retrieves a list of followers based on your actor ID, then sends the activity to each of them.

```python
from activity_handler import ActivityHandler

actor_id = "https://noah.netlify.app/noah/actor.json"
private_key_path = "..."

post_id = "some_id"
content = "some_content"
public = True

handler = ActivityHandler(
    actor_id=actor_id, 
    private_key_path=private_key_path
)

handler.send_publish_activity(
    post_id=post_id,
    content=content,
    public=public
)
```

### Example: Delete Activity

To delete a specific post, use the post ID and send a delete activity to all your followers. Note that once a post is deleted, you cannot reuse the same post ID. Consider updating the content or visibility of the post instead of deleting it.

```python
from activity_handler import ActivityHandler

actor_id = "https://noah.netlify.app/noah/actor.json"
private_key_path = "..."

post_id = "some_id"

handler = ActivityHandler(
    actor_id=actor_id, 
    private_key_path=private_key_path
)

handler.send_delete_activity(
    post_id=post_id,
)
```

### ActivityHandler {#activity_handler}

```python
from activity_request import *
from activity_generator import ActivityGenerator

class ActivityHandler: 
    def __init__(self, actor_id, private_key_path):
        self.actor_id = actor_id
        self.generator = ActivityGenerator.get_instance()
        self.handler = ActivityPubRequestHandler(actor_id, private_key_path)
        
    def send_follow_activity(self, webfinger, debug=True):
        activity_dto = self.generator.generate_follow_activity(self.actor_id, webfinger)
        if isinstance(activity_dto, list):
            return activity_dto
        response = self.handler.send_request(activity_dto)
        return self.__interpret_response(activity='Follow', response=response, debug=debug)

    def send_accept_activity(self, webfinger, debug=True):
        activity_dto = self.generator.generate_accept_activity(self.actor_id, webfinger)
        response = self.handler.send_request(activity_dto)
        return self.__interpret_response(activity='Accept', response=response, debug=debug)
    
    def send_publish_activity(self, post_id, content, public=True, debug=True):
        activity_dto = self.generator.generate_publish_activity(self.actor_id, post_id, content, public)
        responses = self.__share_to_follower(activity_dto)
        return self.__interpret_response(activity='Publish', response=responses, debug=debug)
    
    def send_delete_activity(self, post_id, debug=True):
        activity_dto = self.generator.generate_delete_activity(self.actor_id, post_id)
        responses = self.__share_to_follower(activity_dto)
        return self.__interpret_response(activity='Delete', response=responses, debug=debug)

    def __share_to_follower(self, activity_dto):
        responses = []
        for follower in activity_dto.followers:
            domain, inbox_url, inbox_endpoint = follower
            activity_dto.domain = domain
            activity_dto.inbox_url = inbox_url
            activity_dto.inbox_endpoint = inbox_endpoint
            responses.append(self.handler.send_request(activity_dto))
        return responses

    def __interpret_response(self, activity, response, debug=True):
        if not debug:
            return response
        if activity in ["Follow", "Accept"]:
            if response.ok:
                print(f'\n{activity} activity successfully operated!\n')
                print(response.text)
            else:
                print(f'\nUnsuccessful {activity} activity')
                print(f'Status code: {response.status_code}')
                print(f'Reason: {response.reason}')
            return response
        
        success = 0
        failure = 0
        for item in response:
            if item.ok:
                success += 1
                print(f'\n{activity} activity successfully operated!\n')
                print(item.text)
            else:
                failure += 1
                print(f'\nUnsuccessful {activity} activity')
                print(f'Status code: {item.status_code}')
                print(f'Reason: {item.reason}')
                print(item.text)
            
        total = success + failure
        print(f"\nOverall")
        print(f"Success: {success}")
        print(f"Failure: {failure}")
        print(f"Total: {total}")
        return response
```

### ActivityGenerator {{#activity_generator}}

```python
from datetime import datetime, timezone 
from utility import extract_followers_inbox, get_follower_url, ActivityDTO
from actor_info_retriever import *

class ActivityGenerator: 
    instance = None
    def get_instance():
        if ActivityGenerator.instance == None: 
            ActivityGenerator.instance = ActivityGenerator()
        return ActivityGenerator.instance
    
    def generate_follow_activity(self, actor_id, webfinger):
        template = FollowActivityTemplate(actor_id)
        return template.create(webfinger)
        
    def generate_accept_activity(self, actor_id, webfinger):
        template = AcceptActivityTemplate(actor_id)
        return template.create(webfinger)
      
    def generate_publish_activity(self, actor_id, post_id, content, public):
        template = PublishActivityTemplate(actor_id, post_id, content, public)
        return template.create()

    def generate_delete_activity(self, actor_id, post_id):
        template = DeleteActivityTemplate(actor_id, post_id)
        return template.create()

class ActivityTemplate:
    def __init__(self, actor_id, follower_url=None):
        self.actor_id = actor_id
        self.follower_url = follower_url 
        self.__init_info_retriever()

    def create(self, webfinger=None):
        base = self.__get_base_activity(webfinger)
        if isinstance(base, list): 
            return base
        base.activity = self.create_json_activity(base)
        self.extract_followers_inbox(base)
        return base
    
    def __get_base_activity(self, webfinger):
        if webfinger == None:
            return ActivityDTO()

        username, domain = webfinger.split("@")[1:]
        # Retrieve information from webfinger
        values = self.__get_webfinger_info(username, domain)
        if len(values) != 3:
            return values
        target_actor_id, inbox_url, inbox_endpoint = values
        return ActivityDTO(domain, target_actor_id, inbox_url, inbox_endpoint)

    def __init_info_retriever(self):
        self.retriever = ActorObjectInfoRetriever()
        self.retriever.next = ActorInboxInfoRetriever()

    def __get_webfinger_info(self, username, domain):
        return self.retriever.get_info([username, domain])

    def create_json_activity(self, base):
        ...
    
    def extract_followers_inbox(self, base):
        if self.follower_url == None:
            return
        extract_followers_inbox(self.follower_url, base)


class FollowActivityTemplate(ActivityTemplate):
    def __init__(self, actor_id):
        super().__init__(actor_id=actor_id)
    
    def create_json_activity(self, base):
        activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Follow",
            "actor": self.actor_id,
            "object": base.target_actor_id
        }
        return activity

class AcceptActivityTemplate(ActivityTemplate):
    def __init__(self, actor_id):
        super().__init__(actor_id=actor_id)
    
    def create_json_activity(self, base):
        activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Accept",
            "actor": self.actor_id,
            "object": base.target_actor_id
        }
        return activity

class PublishActivityTemplate(ActivityTemplate):
    def __init__(self, actor_id, post_id, content, public):
        self.post_id = post_id
        self.content = content
        self.public = public
        super().__init__(actor_id, get_follower_url(actor_id))
        
    def create_json_activity(self, base):
        date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Create",
            "id": self.post_id,
            "actor": self.actor_id,
            "object": {
                "id": self.post_id,
                "type": "Note", 
                "published": date,
                "content": self.content,
                "attributedTo": self.actor_id,
                "to": [ self.follower_url],
                "cc": [ self.follower_url]
            },
            "to": [ self.follower_url],
            "cc": [ self.follower_url]
        }
        if self.public:
            public_flag = "https://www.w3.org/ns/activitystreams#Public"
            activity["object"]['to'].append(public_flag)
            activity['to'].append(public_flag)
        return activity

class DeleteActivityTemplate(ActivityTemplate):
    def __init__(self, actor_id, post_id):
        self.post_id = post_id
        super().__init__(actor_id, get_follower_url(actor_id))
        
    def create_json_activity(self, base):
        activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Delete",
            "actor": self.actor_id,
            "object": self.post_id
        }
        return activity
```

### ActivityRequest {{#activity_request}}
```python
import requests
import base64
import json
import hashlib
from datetime import datetime, timezone
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

class ActivityPubRequestHandler:
    def __init__(self, actor_id, private_key_path):
        self.actor_id = actor_id
        self.private_key_path = private_key_path
        self.private_key = self.__load_private_key()

    def __load_private_key(self) -> None:
        with open(self.private_key_path, "rb") as key_file:
            private_key = load_pem_private_key(key_file.read(), password=None)
        return private_key

    def send_request(self, activity_dto):
        # Gather information
        domain = activity_dto.domain
        inbox_url = activity_dto.inbox_url
        inbox_endpoint = activity_dto.inbox_endpoint
        activity = activity_dto.activity

        # Convert Activity to JSON 
        activity = json.dumps(activity)
        
        # Generates Headers
        headers = self.__generate_headers(domain, activity, inbox_endpoint)
       
        return self.__send_post_request(inbox_url, headers, activity)
    
    # Support functions for send_activity
    def __generate_headers(self, domain, activity, inbox_endpoint): 
        headers = { "Content-Type": "application/activity+json"}
    
        headers['Host'] = domain

        date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        headers['Date'] = date

        digest = self.__generate_digest(activity)
        headers['Digest'] = digest
         
        headers['Signature'] = self.__generate_signature(headers, inbox_endpoint)
        return headers

    def __generate_digest(self, activity: str) -> str:
        sha256 = hashlib.sha256()
        sha256.update(activity.encode('utf-8'))
        digest = base64.b64encode(sha256.digest()).decode('utf-8')
        return f"SHA-256={digest}"
        
    def __generate_signature(self, headers, inbox_endpoint):
        sign_string = f'(request-target): post {inbox_endpoint}\n'
        sign_string += f'host: {headers["Host"]}\n'
        sign_string += f'date: {headers["Date"]}\n'
        sign_string += f'digest: {headers["Digest"]}'
        
        signature = self.private_key.sign(
            sign_string.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        signature = base64.b64encode(signature).decode('utf-8')

        key_id = f"{self.actor_id}#main-key"
        signature_header = (
        f'keyId="{key_id}",'
        f'headers="(request-target) host date digest",'
        f'signature="{signature}",'
        f'algorithm="rsa-sha256"'
        )
        
        return signature_header

    def __send_post_request(self, url, headers, activity):
        return requests.post(url, headers=headers, data=activity)
```

### ActorInfoRetriever {{#actor_info_retriever}}
```python
import requests 
import json

class ActorInfoRetriever:
    def __init__(self, next=None):
        self.next = next
    
    def set_next(self, next): 
        self.next = next

    def get_info(self, info):
        value = self.retrieve(info) 
        if len(value) == 0:
            return []
        return value + self.__get_next(value[-1])

    def retrieve(self, info):
        return []

    def __get_next(self, info ):
        if self.next == None: 
            return [] 
        return self.next.get_info(info)

    def send_get_request(self, url="", headers={}, params={}): 
        if url == "":
            return None
        
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
```

### Utility {{#utility}}

```python
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
    follower_ids = __get_followers_id(follower_url)
    __add_outbox_to_url(follower_ids)
    followers = []
    for follower_id in follower_ids:
        domain= follower_id.split("/")[2]
        # Getting inbox endpoint
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
``` 

---
**See also** 
- [Running ActivityPub Server on Static Site](/page/running_activitypub_server_leveraging_static_web_hosting/)
