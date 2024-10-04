import unittest
import os

from modules.handler.resource_handler import ResourceHandler
from modules.handler.config_data_handler import ConfigDataHandler
from tests.utility import make_test_folder, tear_down_test_folders, read_from_json

class ResourceHandlerTest(unittest.TestCase):
	@classmethod
	def setUp(cls):
		make_test_folder()
		cls.handler = ResourceHandler("tests/resources/users")
		
	def tearDown(self):
		tear_down_test_folders()

	def test_create_directory(self):
		username = "simon" 
		domain = "test.example.com"
		self.handler.create_user_directory(username, domain)
		self.assertTrue(os.path.isdir(f"tests/resources/users/{username}"))
		self.assertTrue(os.path.isfile(f"tests/resources/users/{username}/replies.json"))
		self.assertTrue(os.path.isfile(f"tests/resources/users/{username}/followers.json"))
		self.assertTrue(os.path.isfile(f"tests/resources/users/{username}/following.json"))
		self.assertTrue(os.path.isfile(f"tests/resources/users/{username}/posts.json"))

	def test_create_already_exists_directory(self):
		username = "noah" 
		domain = "staticap.netlify.app"
		self.handler.create_user_directory(username, domain)
		self.assertTrue(os.path.isdir(f"tests/resources/users/{username}"))
		self.assertTrue(os.path.isfile(f"tests/resources/users/{username}/replies.json"))
		self.assertTrue(os.path.isfile(f"tests/resources/users/{username}/followers.json"))
		self.assertTrue(os.path.isfile(f"tests/resources/users/{username}/following.json"))
		self.assertTrue(os.path.isfile(f"tests/resources/users/{username}/posts.json"))

	def test_add_follower(self):
		webfinger = "@test@webfinger"
		self.handler.add_follower(webfinger)
		data = read_from_json("tests/resources/users/noah/followers.json")
		self.assertIsNotNone(data)
		self.assertTrue(webfinger in data.get("webfingers"))
		self.handler.add_follower(webfinger)
		data = read_from_json("tests/resources/users/noah/followers.json")
		self.assertEqual(1, len(data.get("webfingers")))

	def test_add_then_remove_follower(self):
		webfinger = "@test@webfinger"
		self.handler.add_follower(webfinger)
		data = read_from_json("tests/resources/users/noah/followers.json")
		self.assertIsNotNone(data)
		self.assertTrue(webfinger in data.get("webfingers"))
		self.handler.remove_follower(webfinger)
		data = read_from_json("tests/resources/users/noah/followers.json")

	def test_remove_empty_follower(self):
		webfinger = "@test@webfinger"
		self.handler.remove_follower(webfinger)
		data = read_from_json("tests/resources/users/noah/followers.json")
		self.assertEqual(0, len(data.get("webfingers")))

	def test_add_following(self):
		webfinger = "@test@webfinger"
		self.handler.add_following(webfinger)
		data = read_from_json("tests/resources/users/noah/following.json")
		self.assertIsNotNone(data)
		self.assertTrue(webfinger in data.get("webfingers"))
		self.handler.add_following(webfinger)
		data = read_from_json("tests/resources/users/noah/following.json")
		self.assertEqual(1, len(data.get("webfingers")))

	def test_add_then_remove_following(self):
		webfinger = "@test@webfinger"
		self.handler.add_following(webfinger)
		data = read_from_json("tests/resources/users/noah/following.json")
		self.assertIsNotNone(data)
		self.assertTrue(webfinger in data.get("webfingers"))
		self.handler.remove_following(webfinger)
		data = read_from_json("tests/resources/users/noah/following.json")
		self.assertEqual(0, len(data.get("webfingers")))

	def test_remove_empty_following(self):
		webfinger = "@test@webfinger"
		self.handler.remove_following(webfinger)
		data = read_from_json("tests/resources/users/noah/following.json")
		self.assertEqual(0, len(data.get("webfingers")))
		...

	def test_add_post(self):
		post_id = "post_id"
		self.handler.add_post(post_id)
		data = read_from_json("tests/resources/users/noah/posts.json")
		self.assertIsNotNone(data)
		self.assertTrue(post_id in data.get("posts"))
		self.handler.add_post(post_id)
		data = read_from_json("tests/resources/users/noah/posts.json")
		self.assertEqual(1, len(data.get("posts")))

	def test_add_then_remove_post(self):
		post_id = "post_id"
		self.handler.add_post(post_id)
		data = read_from_json("tests/resources/users/noah/posts.json")
		self.assertIsNotNone(data)
		self.assertTrue(post_id in data.get("posts"))
		self.handler.remove_post(post_id)
		data = read_from_json("tests/resources/users/noah/posts.json")
		self.assertEqual(0, len(data.get("posts")))

	def test_remove_empty_posts(self):
		post_id = "post_id"
		self.handler.remove_post(post_id)
		data = read_from_json("tests/resources/users/noah/posts.json")
		self.assertEqual(0, len(data.get("posts")))

	def test_add_reply(self):
		post_id = "post_id"
		self.handler.add_reply(post_id, 'testing')
		data = read_from_json("tests/resources/users/noah/replies.json")
		self.assertIsNotNone(data)
		self.assertEqual(0, data.get("posts")[0]['id'])
		self.assertEqual('testing', data.get("posts")[0]['content'])
		self.assertTrue(post_id in data.get("posts")[0].get("in_reply_to_id"))
		self.assertEqual(1, data.get("reply_count"))


