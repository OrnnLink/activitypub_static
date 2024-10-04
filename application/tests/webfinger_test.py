import unittest
import os

from modules.handler.webfinger_handler import WebfingerHandler
from modules.handler.webfinger_handler import ConfigDataHandler
from tests.utility import make_test_folder, tear_down_test_folders, read_from_json

class WebfingerHandlerTest(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		make_test_folder()
		cls.handler = WebfingerHandler()
		
	def tearDown(self):
		tear_down_test_folders()
		...
    
	def __verify(self, username, domain):
		self.__verify_domain_in_hugo_toml(domain=domain)
		actor_id = self.__verify_webfinger_created(username, domain)
		self.__verify_actor_id_created(username, actor_id)
		self.__verify_support_files_created(username, actor_id)
	
	def __verify_domain_in_hugo_toml(self, domain):
		with open("tests/activitypub/hugo.toml", "r") as fd:
			data = fd.readlines()
		data = [ line.strip() for line in data]
		
		for line in data:
			if "baseURL" in line:
				self.assertEqual(f"baseURL = 'https://{domain}/'", line)
				break
	
	def __verify_webfinger_created(self, username, domain):
		webfinger = f"{username}@{domain}"
		filename = "tests/activitypub/static/.well-known/webfinger"
		self.assertTrue(os.path.isdir("tests/activitypub/static/.well-known"))
		data = read_from_json(filename)
		self.assertIsNotNone(data)
		actor_id = f"https://{domain}/{username}/user-info/actor.json"
		expected = {
			"aliases": [],
			"links": [
				{
					"rel": "self",
					"href": actor_id,
					"type": "application/activity+json"
				}
			],
			"subject": f"acct:{webfinger}"
		}
		self.assertEqual(expected.keys(), data.keys())
		self.assertEqual(expected.get("aliases"), data.get('aliases'))
		self.assertEqual(expected.get("subject"), data.get('subject'))
		self.assertEqual(expected.get("links")[0].get("rel"), data.get('links')[0].get("rel"))
		self.assertEqual(expected.get("links")[0].get("href"), data.get('links')[0].get("href"))
		self.assertEqual(expected.get("links")[0].get("type"), data.get('links')[0].get("type"))
		return actor_id
		
	def __verify_actor_id_created(self, username, actor_id):
		follower_url = actor_id.replace("actor", "followers")
		follwing_url  = actor_id.replace("actor", "following")
		inbox_url = actor_id.replace("actor", "inbox")
		outbox_url = actor_id.replace("actor", "outbox")
		with open(ConfigDataHandler.get_instance().public_key_path, "r") as fd:
			publicKey = fd.readlines()
		publicKey = "\n".join([line.strip() for line in publicKey])
		self.assertTrue(os.path.isdir(f"tests/activitypub/static/{username}"))
		self.assertTrue(os.path.isdir(f"tests/activitypub/static/{username}/user-info"))
		self.assertTrue(os.path.isdir(f"tests/activitypub/static/{username}/content"))
		self.assertTrue(os.path.isdir(f"tests/activitypub/static/{username}/replies"))
		data = read_from_json(f"tests/activitypub/static/{username}/user-info/actor.json")
		self.assertIsNotNone(data)
		expected = {
			"@context": [
				"https://www.w3.org/ns/activitystreams"
			],
			"endpoints": {
				"sharedInbox": inbox_url
			},
			"id": actor_id,
			"type": "Person",
			"preferredUsername": username,
			"name": username,
			"inbox": inbox_url ,
			"outbox": outbox_url ,
			"followers": follower_url ,
			"following": follwing_url,
			"manuallyApprovesFollowers": False,
			"publicKey": {
				"@context": "https://w3id.org/security/v1",
				"@type": "key",
				"id": f"{actor_id}#main-key",
				"owner": actor_id,
				"publicKeyPem": publicKey
			}
		}
		self.assertEqual(expected, data)

	def __verify_support_files_created(self, username, actor_id): 
		filenames = [ "followers", "following", "inbox", "outbox"]
		prefix = f"tests/activitypub/static/{username}/user-info"
		for filename in filenames:
			self.assertTrue(os.path.isdir(f"{prefix}/{filename}"))
			filename = f"{prefix}/{filename}.json"
			data = read_from_json(filename)
			self.assertIsNotNone(data)
			expected = {
				
			}

			filename = f"{prefix}/{filename}.json"
			data = read_from_json(filename)
			self.assertIsNotNone(data)
		
	def test_basic_create(self):
		username = 'simon'
		domain = "test.domain.com"
		self.handler.create_user(username, domain)
		self.__verify(username, domain)
		
		...

	
    	