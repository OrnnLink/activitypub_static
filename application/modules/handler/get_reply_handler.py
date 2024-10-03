import json
from datetime import datetime, timedelta
from modules.utility import extract_followers_outbox, send_get_request
from modules.handler.base_handler import BaseHandler

class GetReplyHandler(BaseHandler):
	def get_replies(self) -> list:
		outboxes = extract_followers_outbox(self.follower_url)
		# outboxes = ["https://mstdn.social/users/lowqualityfacts/outbox"]
		posts = self.__retrieve_posts_from_outboxes(outboxes)
		filtered_posts = self.__filtered_posts(posts)
		...

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

	def __retrieve_posts_from_ordered_items(self, ordered_items: list):
		posts = []
		six_months_ago = datetime.now() - timedelta(days=6*30)
		for post in ordered_items:
			published_date = post.get('published', '')
			if published_date:
				published_date = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%SZ")
				if six_months_ago <= published_date <= datetime.now():
					posts.append(post)
				else:
					break
		return posts

	def __retrieve_posts_from_nested_outbox(self, outbox_data: dict):
		total_items = outbox_data['totalItems']
		url = outbox_data['first'] 
		posts = []
		while total_items != 0:
			response = send_get_request(url)
			data = json.loads(response.text)
			if "next" in data.keys():
				url = data['next']
			new_posts = self.__retrieve_posts_from_ordered_items(data['orderedItems'])
			if len(new_posts) == 0:
				break
			posts += new_posts
			total_items -= len(data['orderedItems'])
		return posts

	def __filtered_posts(self, posts: list) -> None:
		filtered_posts = []
		for post in posts:
			object_map = post.get("object", "")
			if not object_map:
				continue

			if isinstance(object_map, str):
				print(post)
		...



