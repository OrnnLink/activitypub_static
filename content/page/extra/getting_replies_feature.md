+++
title = 'Getting Replies Feature'
date = 2024-08-09T16:46:50+10:00
draft = false
+++

Given there exists a mutual relationship between your static site actor, and other ActivityPub platform user. Many ActivityPub platforms send out a `HTTP POST` request to your actor inbox, whenever the other actor publish new content that is relevant to you. Because our site is static by nature, we will not be able to actively listen for the requests and take appropriate action. Despite this, there are alternative measures we can take to solve this problems. For our case, we use the `outbox` of our list of followers and following, in `followers.json` & `following.json` respectively, make a `HTTP GET` request to retrieve a list of post and filter them out accordingly.

Here is an example code:
```python
import requests
import json

from utility import get_follower_url, extract_followers_outbox, ActivityDTO

class PostReplyHandler:
    def __init__(self, actor_id, webfinger):
        self.actor_id = actor_id
        self.domain, self.username = webfinger.split("@")[1:]

    def get_replies(self):
        # Getting a list of followers
        activity_dto = ActivityDTO()
        follower_url = get_follower_url(self.actor_id)
        extract_followers_outbox(follower_url, activity_dto)
        
        filtered_posts = []
        for follower in activity_dto.followers:
            outbox_url  = follower[1]
            posts = self.__get_posts(outbox_url)
            filtered_posts.append(self.__filtered_post(posts))
        return filtered_posts
    
    def __get_posts(self, outbox_url):
        headers = { "accept": "application/activity+json" } 
        response = requests.get(outbox_url, headers=headers)
        
        if not response.ok: 
            return []
        
        data = json.loads(response.text)
        if 'orderedItems' in data.keys():
            return self.__get_post_from_ordered_items(data)
        elif "first" in data.keys():
            first = data['first']
            if isinstance(first, dict):
                return self.__get_post_from_ordered_items(first)
                
        return self.__get_post_from_ext_urls(data)
         
    def __get_post_from_ordered_items(self, data): 
            items = data['orderedItems']
            posts = []
            urls = []
            for item in items: 
                if type(item) == str:
                    # This couldbe urls leading to more problems
                    urls.append(item)

                elif type(item) == dict: 
                    posts.append(json.loads(item))
                    
            for url in urls:
                headers = { "accept": "application/activity+json"}
                response = requests.get(url, headers=headers)
                if not response.ok:
                    continue
                posts.append(json.loads(response.text))
            
            if "next" in data.keys():
                posts += self.__get_post_from_ext_urls(data)
            return posts
            
    def __get_post_from_ext_urls(self, data):
        excluded_keys = [ "@context", "id", "type", "totalItems", "orderedItems"] 
        urls = []
        # Getting relevant urls
        for key in data:
            if key not in excluded_keys:
                urls.append(data[key])
        
        posts = [] 
        while len(urls) != 0:
            url = urls.pop(0)
            if isinstance(url, dict):
                for data in url['orderedItems']:
                    if isinstance(data, str):
                        urls.insert(0, data)
                    else:
                        posts.append(data)
                continue
            response = requests.get(url, headers={ "accept": "application/activity+json"})
            json_data = json.loads(response.text)
            
            if "orderedItems" not in json_data.keys(): 
                break 
            
            for item in json_data['orderedItems']:
                if type(item) == str:
                    urls.append(item)
                elif type(item) == dict: 
                    posts.append(item)

            # Registered the next urls
            if "next" in json_data.keys():
                urls.append(json_data["next"])
            elif "last" in json_data.keys():
                urls.append(json_data["last"])
            else: 
                break
        return posts

    def __filtered_post(self, posts): 
        filtered_posts = []
        for post in posts:
            if 'object' not in post.keys(): 
                continue
            elif post['type'] != "Create":
                continue

            post_obj = post['object']
            if 'inReplyTo' not in post_obj.keys(): 
                continue            
            elif post_obj['inReplyTo'] == None: 
                continue
        
            in_reply_to = post_obj['inReplyTo']
            if self.domain in in_reply_to and self.username in in_reply_to:
                filtered_posts.append(post)
            
        return filtered_posts

if __name__ == "__main__":
    actor_id =  "https://noah.netlify.app/noah/actor.json"

    webfinger = "@noah@netlify.app"
    handler = PostReplyHandler(actor_id, webfinger)
    print(handler.get_replies())

```

---
**See also**
- [Running ActivityPub Server on Static Site](/activitypub_static/page/running_activitypub_server_leveraging_static_web_hosting/)
- [Codebase](/activitypub_static/page/extra/activitypub_codebase)


