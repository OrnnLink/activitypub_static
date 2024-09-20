import requests
import json

from modules.utility import get_follower_url, extract_followers_outbox, ActivityDTO
# from utility import get_follower_url, extract_followers_outbox, ActivityDTO

class PostReplyHandler:
    def __init__(self, actor_id, webfinger, single_user=True):
        self.actor_id = actor_id
        self.username, self.domain = webfinger.split("@")[1:]
        self.single_user = single_user

    def get_replies(self):
        static_data = {
            "username": "ylay",
            "domain": "sdlay.netlify.app"
        } 
        # Getting a list of followers
        activity_dto = ActivityDTO()
        follower_url = get_follower_url(self.actor_id)
        extract_followers_outbox(follower_url, activity_dto)
        all_posts = []
        print()
        for follower in activity_dto.followers:
            print(f"Going through {follower[-1]}")
            if static_data['username']in follower[1] and static_data['domain'] in follower[1]: 
                continue
            outbox_url  = follower[1]
            posts = self.__get_posts(outbox_url)
            filtered_posts = self.__filtered_post(posts)
            all_posts += filtered_posts
        return all_posts

    def __get_posts(self, outbox_url):
        headers = { "accept": "application/activity+json" } 
        response = requests.get(outbox_url, headers=headers)
        
        # This only occurs if the instance hasn't create the outbox properly
        # if not response.ok: 
        #     return []
        
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
            if items == None:
                return []

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
            if type(post_obj) == str: 
               in_reply_to = post_obj 
            if 'inReplyTo' not in post_obj.keys(): 
                continue            
            elif post_obj['inReplyTo'] == None: 
                continue
            else:
                in_reply_to = post_obj['inReplyTo']
        
            if self.domain in in_reply_to:
                if self.single_user:
                    filtered_posts.append(post)
                elif self.username in in_reply_to:
                    filtered_posts.append(post)
        return filtered_posts

