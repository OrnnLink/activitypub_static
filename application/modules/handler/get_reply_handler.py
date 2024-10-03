from modules.utility import extract_followers_outbox
from modules.handler.base_handler import BaseHandler

class GetReplyHandler(BaseHandler):
	def get_replies(self) -> list:
		print(self.follower_url)
		print(extract_followers_outbox(self.follower_url))
		...

	def __filtered_replies(self, replies: list) -> None:
		...



