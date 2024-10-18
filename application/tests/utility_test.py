import unittest
from modules.utility import *

class UtiltyTest(unittest.TestCase):
	def setUp(self):
		self.username = "noah"
		self.domain = "staticap.netlify.app"

	def test_extract_static_follower_outbox(self):
		url = f"https://{self.domain}/{self.username}/user-info/followers.json"
		outboxes = extract_followers_outbox(url)
		data = json.loads(send_get_request(url).text)
		data = json.loads(send_get_request(data['first']).text)
		self.assertEqual(len(data.get("orderedItems")), len(outboxes))
		expected = data.get("orderedItems")
		for i in range(len(expected)):
			self.assertEqual(f"{expected[i]}/outbox", outboxes[i].outbox_url)

	def test_extract_static_follower_inbox(self):
		url = f"https://{self.domain}/{self.username}/user-info/followers.json"
		inboxes = extract_followers_inbox(url)
		data = json.loads(send_get_request(url).text)
		data = json.loads(send_get_request(data['first']).text)
		self.assertEqual(len(data.get("orderedItems")), len(inboxes))
		expected = data.get("orderedItems")
		for i in range(len(expected)):
			self.assertEqual(f"{expected[i]}/inbox", inboxes[i].inbox_url)

	# def test_extract_basic_inbox(self):		
	# 	url = f"https://paul.kinlan.me/followers"
	# 	inboxes = extract_followers_inbox(url)
	# 	data = json.loads(send_get_request(url).text)
	# 	self.assertEqual(len(data.get("orderedItems")), len(inboxes))
	# 	expected = data.get("orderedItems")
	# 	for i in range(len(expected)):
	# 		self.assertEqual(f"{expected[i]}/inbox", inboxes[i].inbox_url)


