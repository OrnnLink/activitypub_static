import os
from modules.utility import make_directory, write_to_json
from modules.handler.config_data_handler import ConfigDataHandler

class WebfingerHandler:
    def __init__(self):
        self.config_handler = ConfigDataHandler.get_instance()
        
    def create_user(self, username, domain):           
        if domain != "":
            self.__update_domain_in_hugo(domain)

        if username != self.config_handler.username:
            self.make_webfinger(username)
            self.make_actor_object(username)
            actor_id = f"https://{self.config_handler.domain}/{username}/user-info"
            self.__make_actor_info_files(username, actor_id)
            self.__update_netlify_toml(username) 

    def make_webfinger(self, username):
        self.__make_webfinger_dirs()
        template = {
            "aliases": [],
            "links": [
                {
                    "href": f"https://{self.config_handler.domain}/{username}/user-info/actor.json",
                    "rel": "self",
                    "type": "application/activity+json"
                },
            ],
            "subject": f"acct:{username}@{self.config_handler.domain}"
        }
        filename = f"{self.config_handler.static_dir_path}/.well-known/webfinger"
        write_to_json(template, filename)
    
    def __update_netlify_toml(self, username):
        path = self.config_handler.root_dir_path + "/netlify.toml"
        with open(path, "r") as fd:
            data = fd.readlines()
        for line in data:
            if "for" in line and username in line:
                return

        data.append("[[headers]]\n")
        data.append(f'for = "/{username}/*"\n')
        data.append("[headers.values]\n")
        data.append('Content-Type = "application/activity+json; charset=utf-8"\n\n')
        with open(path, "w") as fd:
            fd.writelines(data)
        
    
    def __update_domain_in_hugo(self, domain):
        self.config_handler.domain = domain
        filename = f"{self.config_handler.site_dir_path}/hugo.toml"
        with open(filename, "r") as fd:
            data = fd.readlines()
        data = [line.strip() for line in data] 
        with open(filename, "w") as fd:
            for i, line in enumerate(data):
                if "baseURL" in line:
                    data[i] = f"baseURL = 'https://{domain}/'"
                fd.write(data[i] + "\n")
    
    def __make_webfinger_dirs(self):
        dirname = f"{self.config_handler.static_dir_path}/.well-known"
        make_directory(dirname)

        return self
     
    def make_actor_object(self, username):
        self.__make_actor_json_files(username)
        actor_id = f"https://{self.config_handler.domain}/{username}/user-info"
        with open(self.config_handler.public_key_path, "r") as fd: 
            publicKey = fd.readlines()
        publicKey = "\n".join([line.strip() for line in publicKey]) + "\n"
        # publicKey = "\n".join([line.strip() for line in open(self.config_handler.public_key_path, "r")])
        template = {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/v1",
                {
                  "schema": "http://schema.org#",
                  "PropertyValue": "schema:PropertyValue",
                  "value": "schema:value"
                },
                {
                  "discoverable": "http://joinmastodon.org/ns#discoverable"
                }
            ],
            "endpoints": {
                "sharedInbox": f"{actor_id}/inbox.json"
            },
            "id": f"{actor_id}/actor.json",
            "type": "Person",
            "preferredUsername": f"{username}",
            "name": f"{username}",
            "discoverable": True, 
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
        filename = f"{self.config_handler.static_dir_path}/{username}/user-info/actor.json"
        write_to_json(template, filename)
                        
    def __make_actor_json_files(self, username):
        # makes the username file
        dirname = f"{self.config_handler.static_dir_path}/{username}"
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
            filename = f"{self.config_handler.static_dir_path}/{username}/user-info/{name}"
            write_to_json(template, f"{filename}.json")
            
            template = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "id": f"{actor_id}/{name}/first.json",
                "partOf": f"{actor_id}/{name}.json",
                "type": "OrderedCollectionPage",
                "orderedItems": []
            }
            write_to_json(template, f"{filename}/first.json")
       
