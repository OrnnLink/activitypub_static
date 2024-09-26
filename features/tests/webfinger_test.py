import unittest
import requests
import json
import os
import shutil
from modules.webfinger_handler import *

class StaticSiteWebfingerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.handler = WebfingerHandler()
        cls.username = cls.handler.username
        cls.domain = cls.handler.domain
        cls.public_key_path = cls.handler.public_key_path
        cls.handler.set_site_dir_path(".")
        os.makedirs("static")
        ... 
        
    def tearDown(self):
        # Example: Cleanup after each test (remove a directory, reset a state, etc.)
        if os.path.exists("static"):
            shutil.rmtree("static")
    
    def __verify_webfinger(self, expected: dict, actual: dict):
        self.assertEqual(expected.keys(), actual.keys())
        self.assertEqual(expected['aliases'], actual['aliases'])
        self.assertEqual(expected['subject'], actual['subject'])
        for key in expected['links'][0]:
            self.assertEqual(expected['links'][0][key], actual['links'][0][key])
        
    def test_webfinger_retrieval(self):
        url = f'https://{self.domain}/.well-known/webfinger'
        params = {
            "resource": f"acct:{self.username}@{self.domain}"
        }
        response = requests.get(url, params=params)
        expected =  {
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
        self.assertTrue(response.status_code >= 200 and response.status_code < 300)
        self.__verify_webfinger(expected, json.loads(response.text))
        
    def __verify_body_object(self, expected: dict, actual: dict):
        self.assertEqual(expected.keys(), actual.keys())
        for key in expected:
            values = expected[key]
            if not isinstance(values, dict):
                self.assertEqual(values, actual[key])
                continue
            self.__verify_body_object(values, actual[key])
    
    def test_actor_object_retrieval(self):
        url = f'https://{self.domain}/{self.username}/user-info/actor.json'
        actor_id = f"https://{self.domain}/{self.username}/user-info"
        publicKey = "\n".join([line.strip() for line in open(self.public_key_path, "r")])
        headers = {
            "accept": f"application/activity+json"
        }
        response = requests.get(url, headers=headers)
        expected =  {
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
        self.assertTrue(response.status_code >= 200 and response.status_code < 300)
        self.__verify_body_object(expected, json.loads(response.text))
    
    def test_support_object_retrieval(self):
        actor_id = f"https://{self.domain}/{self.username}/user-info"
        names = [ "outbox", "inbox", "followers", "following"]
        for name in names:
            url = f"{actor_id}/{name}.json"
            response = requests.get(url)
            expected = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "id": f"{actor_id}/{name}.json",
                "type": "OrderedCollection",
                "totalItems": 0,
                "first": f"f{actor_id}/{name}/first.json"
            }
            self.assertTrue(response.status_code >= 200 and response.status_code < 300)
            self.__verify_body_object(expected, json.loads(response.text))
            url = f"{actor_id}/{name}/first.json"
            response = requests.get(url)
            expected = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "id": f"{actor_id}/{name}/first.json",
                "partOf": f"{actor_id}/{name}.json",
                "type": "OrderedCollectionPage",
                "orderedItems": []
            }
            self.assertTrue(response.status_code >= 200 and response.status_code < 300)
            self.__verify_body_object(expected, json.loads(response.text))

    def __verify_file_structure_exists(self, username):
        self.assertTrue(os.path.isdir(f"static/{username}"))
        self.assertTrue(os.path.isdir(f"static/{username}/user-info"))

        names = [ "actor", "inbox", "outbox", "followers", "following"]
        for name in names:
            self.assertTrue(os.path.isfile(f"static/{username}/user-info/{name}.json"))
            if name != "actor":
                self.assertTrue(os.path.isdir(f"static/{username}/user-info/{name}"))
                self.assertTrue(os.path.isfile(f"static/{username}/user-info/{name}/first.json"))
    
    def __verify_file_structure_format(self, username, domain):
        self.__verify_actor_object_format(username, domain)
        self.__verify_support_object_format(username, domain)

    def __verify_actor_object_format(self, username, domain):
        actor_id = f"https://{domain}/{username}/user-info"
        publicKey = "\n".join([line.strip() for line in open(self.public_key_path, "r")])
        expected =  {
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
            "publicKey": {
                "@context": "https://w3id.org/security/v1",
                "@type": "key",
                "id": f"{actor_id}/actor.json#main-key",
                "owner": f"{actor_id}/actor.json",
                "publicKeyPem": f"{publicKey}"
            }
        }
        with open(f"static/{username}/user-info/actor.json", "r") as fd:
            result = json.load(fd)
        self.assertEqual(expected, result)
    
    def __verify_support_object_format(self, username, domain):
        actor_id = f"https://{domain}/{username}/user-info"
        names = [ "inbox", "outbox", "followers", "following"]
        for name in names:
            expected = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "id": f"{actor_id}/{name}.json",
                "type": "OrderedCollection",
                "totalItems": 0,
                "first": f"f{actor_id}/{name}/first.json"
            }
            with open(f"static/{username}/user-info/{name}.json", "r") as fd:
                result = json.load(fd)
            self.assertEqual(expected, result)
            expected = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "id": f"{actor_id}/{name}/first.json",
                "partOf": f"{actor_id}/{name}.json",
                "type": "OrderedCollectionPage",
                "orderedItems": []
            }
            with open(f"static/{username}/user-info/{name}/first.json", "r") as fd:
                result = json.load(fd)
            self.assertEqual(expected, result)
        
    def test_create_user_file_created(self):
        username = "bobby" 
        domain = "domain.app"
        self.handler.username = username
        self.handler.domain = domain
        self.handler.create_user()
        self.__verify_file_structure_exists(username)

    def test_create_user_file_created_has_correct_format(self):
        username = "bobby" 
        domain = "domain.app"
        self.handler.username = username
        self.handler.domain = domain
        self.handler.create_user()
        self.__verify_file_structure_format(username, domain)
        


