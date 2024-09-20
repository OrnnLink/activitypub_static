+++
title = 'Signing Algorithm Refactor'
date = 2024-08-02T13:27:24+10:00
draft = false
[prerequisites]
	signing_algorithm = "/extra/signing_algorithm"
+++

Previously on [Signing Algorithm](/extra/signing_algorithm), it involves multiple steps and function calls to utitlise the algorithm. This article go through refactoring steps on the algorithm under object-oriented programming. Enabling the generation and usage of ActivityPub activity under a single function call.

.You can use the following for quick navigation: 
1. [Usage]({{< relref "#usage" >}}) - insight into how to use the codebase
2. [Activity Handler]({{< relref "#activity_handler" >}}) - insight into the ActivityHandler class
3. [Activity Generator]({{< relref "#activity_generator" >}}) - insight into the ActivityGenerator class
4. [Activity Request]({{< relref "#activity_request" >}}) - insight into ActivityRequest class
5. [Actor Info Retriever]({{< relref "#actor_info_retriever" >}}) - insight into ActorInfoRetriever class
6. [Full Codebase]({{< relref "#full_codebase" >}}) - a preview of the whole codebase combining all the components

The refactoring process is done by converting the algorithm into a more object-oriented approach, and separated the algorithm function into 4 components:
1. **ActivityHandler (Facade)** - the entry point of the algorithm, allowing the user to sends various [Activity](https://www.w3.org/TR/activitypub/#client-to-server-interactions) with a simple function call
2. **ActivityGenerator (Singleton)** - responsibles for generating ActivityPub activity JSON object, provided relevant parameters. Currently support [@Follow](https://www.w3.org/TR/activitypub/#follow-activity-outbox), [@Create](https://www.w3.org/TR/activitypub/#create-activity-outbox) and [@Delete](https://www.w3.org/TR/activitypub/#delete-activity-outbox)
3. **ActivityRequest** - responsibles for generating and organising information to ensure the structure of the HTTP request is correct, before sending
4. **ActorInfoRetriever (Chain of Responsibility)** - chain of information retrievers used to extra relevant information related to a particular actor to complete a request. Currently there are two retrievers implemented:
	- **ActorObjectInfoRetriever** - given the username and domain, this retriever extract the url that leads to the actor object.
	- **ActorInboxInfoRetriever** - used to retrieve the inbox url of a particular ActivityPub actor. It would also extract the endpoint of that particular inbox url.

## Using the codebase {#usage}

To initialise the {{< pretty-code >}}ActivityHandler{{< /pretty-code >}} you need to provide the constructor with:
1. **actor_id** - the url that leads to your actor object in JSON format.
2. **private_key_path** - the path that leads to where your private key is stored.


### Example of Follow Activity

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

### Example of Publish Activity

for publish activity, the {{< pretty-code >}}ActivityHandler{{< /pretty-code >}} would first extract a list of followers based on your actor id, before sends out the activity out to each of them. 

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

### Example of Delete Activity

If you wanted to delete a certain post, using the post id of that post. You can send a delete activity to all your followers.
Please note that, once a post is deleted, you can no longer create a new post under the same post id. Considers changing the content or the visibility of the post instead of deleting.

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

handler.send_delete_activity(
    post_id=post_id,
)
```

## ActivityHandler {#activity_handler}

```python
from activity_request import *
from activity_generator import ActivityGenerator

class ActivityHandler: 
    def __init__(self, actor_id, private_key_path):
        self.actor_id = actor_id
        self.generator = ActivityGenerator.get_instance()
        self.handler = ActivityPubRequestHandler(actor_id, private_key_path)
    
    def send_follow_activity(self, webfinger):
        activity_dto = self.generator.generate_follow_activity(self.actor_id, webfinger)
        response = self.handler.send_request(activity_dto)
        self.__interpret_response(activity='Follow', response=response)

    def send_accept_activity(self, webfinger):
        activity_dto = self.generator.generate_accept_activity(self.actor_id, webfinger)
        print(activity_dto.activity)
        response = self.handler.send_request(activity_dto)
        self.__interpret_response(activity='Accept', response=response)
    
    def send_publish_activity(self, post_id, content, public=True):
        activity_dto = self.generator.generate_publish_activity(self.actor_id, post_id, content, public)
        responses = self.__share_to_follower(activity_dto)
        self.__interpret_response(activity='Publish', response=responses)
    
    def send_delete_activity(self, post_id):
        activity_dto = self.generator.generate_delete_activity(self.actor_id, post_id)
        responses = self.__share_to_follower(activity_dto)
        self.__interpret_response(activity='Delete', response=responses)

    def __share_to_follower(self, activity_dto):
        responses = []
        for follower in activity_dto.followers:
            domain, inbox_url, inbox_endpoint = follower
            activity_dto.domain = domain
            activity_dto.inbox_url = inbox_url
            activity_dto.inbox_endpoint = inbox_endpoint
            responses.append(self.handler.send_request(activity_dto))
        return responses

    def __interpret_response(self, activity, response):
        if activity in ["Follow", "Accept"]:
            if response.ok:
                print(f'\n{activity} activity successfully operated!\n')
                print(response.text)
            else:
                print(f'\nUnsuccessful {activity} activity')
                print(f'Status code: {response.status_code}')
                print(f'Reason: {response.reason}')
            return
        
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
``` 
 
## ActivityGenerator {#activity_generator} 

Inside the generator class, we have also defined {{< pretty-code >}}ActivityDTO{{< /pretty-code >}} that acts as a [Data Transfer Object (DTO)](https://en.wikipedia.org/wiki/Data_transfer_object) passed onto {{< pretty-code >}}ActivityRequest{{< /pretty-code >}}

```python
import json
from datetime import datetime, timezone 
from actor_info_retriever import *

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
 
class ActivityGenerator: 
    instance = None
    def __init__(self):
        self.__init_info_retriever()

    def __init_info_retriever(self):
        self.retriever = ActorObjectInfoRetriever()
        self.retriever.next = ActorInboxInfoRetriever()

    def __get_webfinger_info(self, username, domain):
        return self.retriever.get_info([username, domain])
    
    def get_instance():
        if ActivityGenerator.instance == None: 
            ActivityGenerator.instance = ActivityGenerator()
        return ActivityGenerator.instance
    
    def __get_base_activity(self, webfinger=None):
        if webfinger == None:
            return ActivityDTO()

        username, domain = webfinger.split("@")[1:]
         # Retrieve information from webfinger
        target_actor_id, inbox_url, inbox_endpoint = self.__get_webfinger_info(username, domain)
        return ActivityDTO(domain, target_actor_id, inbox_url, inbox_endpoint)

    def generate_follow_activity(self, actor_id, webfinger):
        base = self.__get_base_activity(webfinger)
        base.activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Follow",
            "actor": actor_id,
            "object": base.target_actor_id
        }
        return base
        
    def generate_accept_activity(self, actor_id, webfinger):
        base = self.__get_base_activity(webfinger)
        base.activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Accept",
            "actor": actor_id,
            "object": base.target_actor_id
        }
        return base
        
    def generate_publish_activity(self, actor_id, post_id, content, public):
        base = self.__get_base_activity()
        date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        follower_url = self.__get_follower_url(actor_id)
        activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Create",
            "id": post_id,
            "actor": actor_id,
            "object": {
                "id": post_id,
                "type": "Note", 
                "published": date,
                "content": content,
                "attributedTo": actor_id,
                "to": [ follower_url],
                "cc": [ follower_url]
            },
            "to": [ follower_url],
            "cc": [ follower_url]
        }
        if public:
            public_flag = "https://www.w3.org/ns/activitystreams#Public"
            activity["object"]['to'].append(public_flag)
            activity['to'].append(public_flag)

        base.activity = activity
        self.__extract_followers(follower_url, base) 
        return base

    def generate_delete_activity(self, actor_id, post_id):
        base = self.__get_base_activity()
        follower_url = self.__get_follower_url(actor_id)
        activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Delete",
            "actor": actor_id,
            "object": post_id
        }

        base.activity = activity
        self.__extract_followers(follower_url, base) 
        return base

    # Support functions
    def __extract_followers(self, follower_url, activity_dto):
        follower_ids = self.__get_followers_id(follower_url)
        self.__clean_follower_ids(follower_ids)
        followers = []
        for follower_id in follower_ids:
            domain= follower_id.split("/")[2]
            # Getting inbox endpoint
            inbox_endpoint = follower_id.split("/")[3:]
            inbox_endpoint = "/" + "/".join(inbox_endpoint)
            followers.append([domain, follower_id, inbox_endpoint])
        activity_dto.followers = followers
        
    def __get_follower_url(self, actor_id): 
        response = requests.get(actor_id, headers={ "accept": "application/activity+json"})
        data = json.loads(response.text)
        return data['followers']

    def __clean_follower_ids(self, follower_ids):
        for i, follower_id in enumerate(follower_ids):
            if "inbox" not in follower_id:
                if "/" != follower_id[-1]:
                    follower_id += "/"
                follower_id += "inbox"
                follower_ids[i] = follower_id

    def __get_followers_id(self, follower_url):
        response = requests.get(follower_url, headers={ "accept": "application/activity+json"})     
        data = json.loads(response.text)
        
        if "orderedItems" in data:
            return self.__get_follower_from_ordered_items(data)
        return self.__get_follower_from_ext_urls(data)
    
    # Simple case
    def __get_follower_from_ordered_items(self, data): 
        items = data['orderedItems']
        follower_ids = []
        for item in items: 
            if type(item) == str:
                follower_ids.append(item)
            elif type(item) == dict: 
                follower_ids.append(item['id'])
        return items
        
    def __get_follower_from_ext_urls(self, data):
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

## ActivityRequest {#activity_request}

```python
import requests
import base64
import json
import hashlib
from datetime import datetime, timezone
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
    
from actor_info_retriever import *    

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
        print(sign_string)
        
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

## ActorInfoRetriever {#actor_info_retriever}


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
        response = self.send_get_request(info)
        if not response.ok:
            return [ f"Unable to retrieve inbox: {response.reason}"]
    
        data = json.loads(response.text)
        inbox = data['inbox']
        inbox_endpoint = inbox.split("/")[3:]
        return [ inbox, "/" + "/".join(inbox_endpoint)]
```

## Combined Codebase {#full_codebase}
```python
import requests
import json
import base64
import hashlib
from datetime import datetime, timezone
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# Actor Info Retriever
class ActorInfoRetriever:
    def __init__(self, next=None):
        self.next = next
    
    def set_next(self, next): 
        self.next = next

    def get_info(self, info):
        value = self.retrieve(info) 
        if not value:
            return []
        return value + self.__get_next(value[-1])

    def retrieve(self, info):
        return []

    def __get_next(self, info):
        if self.next is None: 
            return [] 
        return self.next.get_info(info)

    def send_get_request(self, url="", headers=None, params=None): 
        if url == "":
            return None
        
        headers = headers or {"accept": "application/activity+json"}

        return requests.get(url, headers=headers, params=params)
    
class ActorObjectInfoRetriever(ActorInfoRetriever):
    def retrieve(self, info):
        username, domain = info
        url = f'https://{domain}/.well-known/webfinger'
        params = {"resource": f"acct:{username}@{domain}"}
        response = self.send_get_request(url, params=params)
        
        if not response.ok:
            return [f"Unable to retrieve actor object: {response.reason}"]
        
        data = json.loads(response.text)
        links = data['links']
        for link in links:
            if link['rel'] == "self":
                return [link['href']]
        
class ActorInboxInfoRetriever(ActorInfoRetriever):
    def retrieve(self, info):
        response = self.send_get_request(info)
        if not response.ok:
            return [f"Unable to retrieve inbox: {response.reason}"]
    
        data = json.loads(response.text)
        inbox = data['inbox']
        inbox_endpoint = inbox.split("/")[3:]
        return [inbox, "/" + "/".join(inbox_endpoint)]

# Activity Request
class ActivityPubRequestHandler:
    def __init__(self, actor_id, private_key_path):
        self.actor_id = actor_id
        self.private_key_path = private_key_path
        self.private_key = self.__load_private_key()
        self.__init_info_retriever()

    def __load_private_key(self):
        with open(self.private_key_path, "rb") as key_file:
            private_key = load_pem_private_key(key_file.read(), password=None)
        return private_key
    
    def __init_info_retriever(self):
        self.retriever = ActorObjectInfoRetriever()
        self.retriever.set_next(ActorInboxInfoRetriever())

    def send_request(self, activity_dto):
        domain = activity_dto.domain
        inbox_url = activity_dto.inbox_url
        inbox_endpoint = activity_dto.inbox_endpoint
        activity = json.dumps(activity_dto.activity)
        
        headers = self.__generate_headers(domain, activity, inbox_endpoint)
        
        return self.__send_post_request(inbox_url, headers, activity)
    
    def __generate_headers(self, domain, activity, inbox_endpoint): 
        headers = {
            "Content-Type": "application/activity+json",
            "Host": domain,
            "Date": datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'),
            "Digest": self.__generate_digest(activity)
        }
        headers['Signature'] = self.__generate_signature(headers, inbox_endpoint)
        return headers

    def __generate_digest(self, activity):
        sha256 = hashlib.sha256()
        sha256.update(activity.encode('utf-8'))
        digest = base64.b64encode(sha256.digest()).decode('utf-8')
        return f"SHA-256={digest}"
        
    def __generate_signature(self, headers, inbox_endpoint):
        sign_string = (
            f'(request-target): post {inbox_endpoint}\n'
            f'host: {headers["Host"]}\n'
            f'date: {headers["Date"]}\n'
            f'digest: {headers["Digest"]}'
        )
        
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

# Activity Generator
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
 
class ActivityGenerator: 
    instance = None
    def __init__(self):
        self.__init_info_retriever()

    def __init_info_retriever(self):
        self.retriever = ActorObjectInfoRetriever()
        self.retriever.next = ActorInboxInfoRetriever()

    def __get_webfinger_info(self, username, domain):
        return self.retriever.get_info([username, domain])
    
    def get_instance():
        if ActivityGenerator.instance == None: 
            ActivityGenerator.instance = ActivityGenerator()
        return ActivityGenerator.instance
    
    def __get_base_activity(self, webfinger=None):
        if webfinger == None:
            return ActivityDTO()

        username, domain = webfinger.split("@")[1:]
         # Retrieve information from webfinger
        target_actor_id, inbox_url, inbox_endpoint = self.__get_webfinger_info(username, domain)
        return ActivityDTO(domain, target_actor_id, inbox_url, inbox_endpoint)

    def generate_follow_activity(self, actor_id, webfinger):
        base = self.__get_base_activity(webfinger)
        base.activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Follow",
            "actor": actor_id,
            "object": base.target_actor_id
        }
        return base
        
    def generate_accept_activity(self, actor_id, webfinger):
        base = self.__get_base_activity(webfinger)
        base.activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Accept",
            "actor": actor_id,
            "object": base.target_actor_id
        }
        return base
        
    def generate_publish_activity(self, actor_id, post_id, content, public):
        base = self.__get_base_activity()
        date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        follower_url = self.__get_follower_url(actor_id)
        activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Create",
            "id": post_id,
            "actor": actor_id,
            "object": {
                "id": post_id,
                "type": "Note", 
                "published": date,
                "content": content,
                "attributedTo": actor_id,
                "to": [ follower_url],
                "cc": [ follower_url]
            },
            "to": [ follower_url],
            "cc": [ follower_url]
        }
        if public:
            public_flag = "https://www.w3.org/ns/activitystreams#Public"
            activity["object"]['to'].append(public_flag)
            activity['to'].append(public_flag)

        base.activity = activity
        self.__extract_followers(follower_url, base) 
        return base

    def generate_delete_activity(self, actor_id, post_id):
        base = self.__get_base_activity()
        follower_url = self.__get_follower_url(actor_id)
        activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Delete",
            "actor": actor_id,
            "object": post_id
        }

        base.activity = activity
        self.__extract_followers(follower_url, base) 
        return base

    # Support functions
    def __extract_followers(self, follower_url, activity_dto):
        follower_ids = self.__get_followers_id(follower_url)
        self.__clean_follower_ids(follower_ids)
        followers = []
        for follower_id in follower_ids:
            domain= follower_id.split("/")[2]
            # Getting inbox endpoint
            inbox_endpoint = follower_id.split("/")[3:]
            inbox_endpoint = "/" + "/".join(inbox_endpoint)
            followers.append([domain, follower_id, inbox_endpoint])
        activity_dto.followers = followers
        
    def __get_follower_url(self, actor_id): 
        response = requests.get(actor_id, headers={ "accept": "application/activity+json"})
        data = json.loads(response.text)
        return data['followers']

    def __clean_follower_ids(self, follower_ids):
        for i, follower_id in enumerate(follower_ids):
            if "inbox" not in follower_id:
                if "/" != follower_id[-1]:
                    follower_id += "/"
                follower_id += "inbox"
                follower_ids[i] = follower_id

    def __get_followers_id(self, follower_url):
        response = requests.get(follower_url, headers={ "accept": "application/activity+json"})     
        data = json.loads(response.text)
        
        if "orderedItems" in data:
            return self.__get_follower_from_ordered_items(data)
        return self.__get_follower_from_ext_urls(data)
    
    # Simple case
    def __get_follower_from_ordered_items(self, data): 
        items = data['orderedItems']
        follower_ids = []
        for item in items: 
            if type(item) == str:
                follower_ids.append(item)
            elif type(item) == dict: 
                follower_ids.append(item['id'])
        return items
        
    def __get_follower_from_ext_urls(self, data):
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

# Activity Handler
class ActivityHandler: 
    def __init__(self, actor_id, private_key_path):
        self.actor_id = actor_id
        self.generator = ActivityGenerator.get_instance()
        self.handler = ActivityPubRequestHandler(actor_id, private_key_path)
    
    def send_follow_activity(self, webfinger):
        activity_dto = self.generator.generate_follow_activity(self.actor_id, webfinger)
        response = self.handler.send_request(activity_dto)
        self.__interpret_response(activity='Follow', response=response)

    def send_accept_activity(self, webfinger):
        activity_dto = self.generator.generate_accept_activity(self.actor_id, webfinger)
        print(activity_dto.activity)
        response = self.handler.send_request(activity_dto)
        self.__interpret_response(activity='Accept', response=response)
    
    def send_publish_activity(self, post_id, content, public=True):
        activity_dto = self.generator.generate_publish_activity(self.actor_id, post_id, content, public)
        responses = self.__share_to_follower(activity_dto)
        self.__interpret_response(activity='Publish', response=responses)
    
    def send_delete_activity(self, post_id):
        activity_dto = self.generator.generate_delete_activity(self.actor_id, post_id)
        responses = self.__share_to_follower(activity_dto)
        self.__interpret_response(activity='Delete', response=responses)

    def __share_to_follower(self, activity_dto):
        responses = []
        for follower in activity_dto.followers:
            domain, inbox_url, inbox_endpoint = follower
            activity_dto.domain = domain
            activity_dto.inbox_url = inbox_url
            activity_dto.inbox_endpoint = inbox_endpoint
            responses.append(self.handler.send_request(activity_dto))
        return responses

    def __interpret_response(self, activity, response):
        if activity in ["Follow", "Accept"]:
            if response.ok:
                print(f'\n{activity} activity successfully operated!\n')
                print(response.text)
            else:
                print(f'\nUnsuccessful {activity} activity')
                print(f'Status code: {response.status_code}')
                print(f'Reason: {response.reason}')
            return
        
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
```

---
**References**
- [ActivityPub Client-Server Interactions](https://www.w3.org/TR/activitypub/#client-to-server-interactions)
- [ActivityPub Follow Activity](https://en.wikipedia.org/wiki/Data_transfer_object)
- [ActivityPub Create Activity](https://www.w3.org/TR/activitypub/#create-activity-outbox)
- [ActivityPub Delete Activity](https://www.w3.org/TR/activitypub/#delete-activity-outbox)
- [Data Transfer Object](https://en.wikipedia.org/wiki/Data_transfer_object)
- [Facade](https://refactoring.guru/design-patterns/facade)
- [Singleton](https://refactoring.guru/design-patterns/singleton)
- [Chain of Responsibility](https://refactoring.guru/design-patterns/chain-of-responsibility)