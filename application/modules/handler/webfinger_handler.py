import os
from modules.handler.base_handler import BaseHandler
from modules.utility import make_directory, write_to_json

class WebfingerHandler(BaseHandler):
    def create_user(self, username, domain):
        if domain != "":
            self.__update_domain_in_hugo(domain)
        elif username != self.username:
            self.make_webfinger(username)
            self.make_actor_object(username)
            actor_id = f"https://{self.domain}/{username}/user-info"
            self.__make_actor_info_files(username, actor_id)
        
    def make_webfinger(self, username):
        self.__make_webfinger_dirs()
        template = {
            "aliases": [],
            "links": [
                {
                    "href": f"https://{self.domain}/{username}/user-info/actor.json",
                    "rel": "self",
                    "type": "application/activity+json"
                },
            ],
            "subject": f"acct:{self.username}@{self.domain}"
        }
        filename = f"{self.static_dir_path}/.well-known/webfinger"
        write_to_json(template, filename)

    def __update_domain_in_hugo(self, domain):
        self.domain = domain
        filename = f"{self.site_dir_path}/hugo.toml"
        data = [line.strip() for line in open(filename, "r")]
        with open(filename, "w") as fd:
            for i, line in enumerate(data):
                if "baseURL" in line:
                    data[i] = f"baseURL = 'https://{domain}/'"
                fd.write(data[i] + "\n")
    
    def __make_webfinger_dirs(self):
        dirname = f"{self.static_dir_path}/.well-known"
        make_directory(dirname)
        return self
     
    def make_actor_object(self, username):
        self.__make_actor_json_files(username)
        actor_id = f"https://{self.domain}/{username}/user-info"
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
            "preferredUsername": f"{username}",
            "name": f"{username}",
            "inbox": f"{actor_id}/inbox.json",
            "outbox": f"{actor_id}/outbox.json",
            "followers": f"{actor_id}/followers.json",
            "following": f"{actor_id}/following.json",
            "manuallyApprovesFollowers": False,
            "publicKey": {
                "@context": "https://w3id.org/security/v1",
                "@type": "key",
                "id": f"{actor_id}/actor.json#main-key",
                "owner": f"{actor_id}/actor.json",
                "publicKeyPem": f"{publicKey}"
            }
        }
        filename = f"{self.static_dir_path}/{username}/user-info/actor.json"
        write_to_json(template, filename)
                        
    def __make_actor_json_files(self, username):
        # makes the username file
        dirname = f"{self.static_dir_path}/{username}"
        make_directory(dirname)
        make_directory(f"{dirname}/user-info")
        make_directory(f"{dirname}/content")
        make_directory(f"{dirname}/replies")
        
        dirname += "/user-info"
        filenames = [ "actor", "outbox", "inbox", "followers", "following" ]
        for filename in filenames:
            fd = open(f"{dirname}/{filename}.json", "w")
            fd.close()
            
            if filename != "actor" and not os.path.isdir(f"{dirname}/{filename}"):
                make_directory(f"{dirname}/{filename}")
                fd = open(f"{dirname}/{filename}/first.json","w")
                fd.close()
        
    def __make_actor_info_files(self, username:str, actor_id: str ):
        names = [ "outbox", "inbox", "followers", "following" ]
        for name in names:
            template = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "id": f"{actor_id}/{name}.json",
                "type": "OrderedCollection",
                "totalItems": 0,
                "first": f"{actor_id}/{name}/first.json"
            }
            filename = f"{self.static_dir_path}/{username}/user-info/{name}"
            write_to_json(template, f"{filename}.json")
            
            template = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "id": f"{actor_id}/{name}/first.json",
                "partOf": f"{actor_id}/{name}.json",
                "type": "OrderedCollectionPage",
                "orderedItems": []
            }
            write_to_json(template, f"{filename}/first.json")
       