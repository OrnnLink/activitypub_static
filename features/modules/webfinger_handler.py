import json
import os

class WebfingerHandler:
    def __init__(self):
        self.__load_config()

    def __load_config(self):
        filename = "config.json"
        with open(filename, "r") as fd:
            data = json.load(fd)

        self.username = data['username']
        self.domain = data['domain']
        self.public_key_path = data['public_key_path']
        self.set_site_dir_path(data['site_dir_path'])

    def set_site_dir_path(self, path: str):
        self.site_dir_path = path
        self.static_dir_path = f'{self.site_dir_path}/static'
        return self
    
    def __write_json(self, filename: str, data: dict):
        with open(filename, "w") as fd:
            fd.write(json.dumps(data, indent=4))
        
    def create_user(self):
        self.make_webfinger()
        self.make_actor_object()
        
    def make_webfinger(self):
        self.__make_webfinger_dirs()
        template = {
            "aliases": [],
            "links": [
                {
                    "href": f"https://{self.domain}/{self.username}/user-info/actor.json",
                    "rel": "self",
                    "type": "application/activity+json"
                },
            ],
            "subject": f"acct:{self.username}@{self.domain}"
        }
        filename = f"{self.static_dir_path}/.well-known/webfinger"
        self.__write_json(filename, template)

    def __make_webfinger_dirs(self):
        dirname = f"{self.static_dir_path}/.well-known"
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        return self
    
    def make_actor_object(self):
        self.__make_actor_json_files()
        actor_id = f"https://{self.domain}/{self.username}/user-info"
        publicKey = "\n".join([line.strip() for line in open(self.public_key_path, "r")])
        template = {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
            ],
            "endpoints": {
                "sharedInbox": f"{actor_id}/inbox.json"
            },
            "id": f"{actor_id}/actor.json",
            "type": "Person",
            "preferredUsername": f"{self.username}",
            "name": f"{self.username}",
            "inbox": f"{actor_id}/inbox.json",
            "outbox": f"{actor_id}/outbox.json",
            "followers": f"{actor_id}/followers.json",
            "following": f"{actor_id}/following.json",
            "publicKey": {
                "@context": "https://w3id.org/security/v1",
                "@type": "key",
                "id": f"{actor_id}/actor.json#main-key",
                "owner": f"{actor_id}/actor.json",
                "publicKeyPem": f"{publicKey}"
            }
        }
        filename = f"{self.static_dir_path}/{self.username}/user-info/actor.json"
        self.__write_json(filename, template)
        self.__make_actor_info_files(actor_id)
                        
    def __make_actor_json_files(self):
        # makes the username file
        dirname = f"{self.static_dir_path}/{self.username}"
        if not os.path.isdir(dirname): 
            os.makedirs(dirname)
            os.makedirs(f"{dirname}/user-info")
            os.makedirs(f"{dirname}/content")
        
        dirname += "/user-info"
        filenames = [ "actor", "outbox", "inbox", "followers", "following" ]
        for filename in filenames:
            fd = open(f"{dirname}/{filename}.json", "w")
            fd.close()
            
            if filename != "actor" and not os.path.isdir(f"{dirname}/{filename}"):
                os.makedirs(f"{dirname}/{filename}")
                fd = open(f"{dirname}/{filename}/first.json","w")
                fd.close()
        
    def __make_actor_info_files(self, actor_id: str ):
        names = [ "outbox", "inbox", "followers", "following" ]
        for name in names:
            template = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "id": f"{actor_id}/{name}.json",
                "type": "OrderedCollection",
                "totalItems": 0,
                "first": f"{actor_id}/{name}/first.json"
            }
            filename = f"{self.static_dir_path}/{self.username}/user-info/{name}"
            self.__write_json(f"{filename}.json", template)
            
            template = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "id": f"{actor_id}/{name}/first.json",
                "partOf": f"{actor_id}/{name}.json",
                "type": "OrderedCollectionPage",
                "orderedItems": []
            }
            self.__write_json(f"{filename}/first.json", template)
       
        