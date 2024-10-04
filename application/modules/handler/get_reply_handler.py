import json
from datetime import datetime, timedelta
from modules.utility import extract_followers_outbox, send_get_request
from modules.handler.config_data_handler import ConfigDataHandler

class GetReplyHandler:
	def __init__(self):
		self.config_handler = ConfigDataHandler.get_instance()

	def get_replies(self) -> list:
		outboxes = extract_followers_outbox(self.config_handler.follower_url)
		print(outboxes)
		posts = self.__retrieve_posts_from_outboxes(outboxes)
		filtered_posts = self.__filtered_posts(posts)
		return filtered_posts

	def __retrieve_posts_from_outboxes(self, outboxes):
		posts = []
		for outbox in outboxes:
			response = send_get_request(outbox.outbox_url)
			data = json.loads(response.text)
			if "orderedItems" in data.keys():
				posts += self.__retrieve_posts_from_ordered_items(data['orderedItems'])
			else:
				posts += self.__retrieve_posts_from_nested_outbox(outbox_data=data)
		return posts	

	def __retrieve_posts_from_ordered_items(self, ordered_items: list, month_filter=3):
		posts = []
		six_months_ago = datetime.now() - timedelta(days=month_filter*30)
		for post in ordered_items:
			if isinstance(post, str):
				response = send_get_request(post)
				post = json.loads(response.text)
			published_date = post.get('published', '')
			if published_date:
				published_date = datetime.strptime(published_date.split("T")[0], "%Y-%m-%d")
				if six_months_ago <= published_date <= datetime.now():
					posts.append(post)
				else:
					continue
		return posts

	def __retrieve_posts_from_nested_outbox(self, outbox_data: dict):
		url = outbox_data['first'] 
		posts = []
		while True:
			if isinstance(url, str):
				response = send_get_request(url)
				data = json.loads(response.text)
				new_posts = self.__retrieve_posts_from_ordered_items(data['orderedItems'])
			elif isinstance(url, dict):
				data = url
				new_posts = self.__retrieve_posts_from_ordered_items(url['orderedItems'])
			else: 
				continue

			if len(new_posts) == 0:
				break
			posts += new_posts
			if "next" in data.keys():
				url = data['next']
			else:
				break	

		return posts

	def __filtered_posts(self, posts: list) -> None:
		filtered_posts = []
		for post in posts:
			activity_type = post.get('type', '')
			object_map = post.get("object", '')

			if not activity_type or not object_map:
				continue 

			if activity_type.lower() == "announce":
				if (self.config_handler.domain in object_map and self.config_handler.username in object_map):
					filtered_posts.append(post) 
				continue
			elif activity_type.lower() == "create":
				in_reply_to = object_map.get("inReplyTo", "")
				if not in_reply_to:
					continue
				elif (self.config_handler.domain in in_reply_to and self.config_handler.username in in_reply_to):
					filtered_posts.append(post)
		return filtered_posts

	def interpret_reply(self, reply: dict):
		activity_type = reply.get("type", "")
		if not activity_type:
			return
		print(f"\nReply ID: {reply.get('id', '')}")
		print(f"Activity Type: {activity_type}")

		if activity_type.lower() == "announce":
			print(reply.get('object', ''))
		else:
			print(reply['object']['content'])

	def __iterate_dict(self, data, indent=0): 
		for key in data:
			values = data[key]
			if isinstance(values, dict):
				print(f"{key}: ")
				self.__iterate_dict(values, indent+4)
			else:
				print(f"{' ' * indent}{key}: {values}")
