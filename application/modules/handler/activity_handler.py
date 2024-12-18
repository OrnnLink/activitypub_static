from modules.utility import extract_followers_inbox
from modules.handler.config_data_handler import ConfigDataHandler
from modules.generator.activity_generator import ActivityGenerator
from modules.dto.activity_dto import ActivityDTO
from modules.handler.activity_request_handler import ActivityRequestHandler
import json

class ActivityHandler(): 
    def __init__(self):
        self.generator = ActivityGenerator.get_instance()
        self.config_handler = ConfigDataHandler.get_instance()
        self.request_handler = ActivityRequestHandler()
        
    def send_follow_activity(self, webfinger):
        activity_dto = ActivityDTO(webfinger=webfinger)
        activity_dto.activity = self.generator.generate_follow_activity(
            self.config_handler.actor_id, activity_dto
        )
        return self.request_handler.send_request(activity_dto)

    def send_unfollow_activity(self, webfinger):
        activity_dto = ActivityDTO(webfinger=webfinger)
        activity_dto.activity = self.generator.generate_unfollow_activity(
            self.config_handler.actor_id, activity_dto
        )
        return self.request_handler.send_request(activity_dto)
        
    def send_publish_activity(self, post_id, content, public=True):
        activity_dto = ActivityDTO(
            post_id=post_id, content=content, public=public,
            follower_url=self.config_handler.follower_url, username=self.config_handler.username
        )
        activity_dto.activity = self.generator.generate_publish_activity(
            self.config_handler.actor_id, activity_dto
        )
        return self.__share_to_follower(activity_dto) + self.__share_to_following(activity_dto)
    
    def send_update_activity(self, post_id, content, public=True):
        activity_dto = ActivityDTO(
            post_id=post_id, content=content, public=public, 
            follower_url=self.config_handler.follower_url, username=self.config_handler.username
        )
        activity_dto.activity = self.generator.generate_update_activity(
            self.config_handler.actor_id, activity_dto
        )
        return self.__share_to_follower(activity_dto) + self.__share_to_following(activity_dto)
    
    def send_reply_activity(self, id_count, in_reply_to_id, content):
        post_id = f"https://{self.config_handler.domain}/{self.config_handler.username}/replies/reply_{id_count}.json"
        activity_dto = ActivityDTO(
            post_id=post_id, content=content, in_reply_to_id=in_reply_to_id
        )
        activity_dto.activity = self.generator.generate_reply_activity(
            self.config_handler.actor_id, activity_dto
        )
        self.__get_post_info(in_reply_to_id, activity_dto)
        return self.request_handler.send_request(activity_dto)

    def __share_to_follower(self, activity_dto):
        responses = []
        for follower in extract_followers_inbox(self.config_handler.follower_url):
            activity_dto.domain = follower.domain
            activity_dto.inbox_url = follower.inbox_url
            activity_dto.inbox_endpoint = follower.get_inbox_endpoint()
            responses.append(self.request_handler.send_request(activity_dto))
        return responses

    def __share_to_following(self,activity_dto):
        responses = []
        for follower in extract_followers_inbox(self.config_handler.following_url):
            activity_dto.domain = follower.domain
            activity_dto.inbox_url = follower.inbox_url
            activity_dto.inbox_endpoint = follower.get_inbox_endpoint()
            responses.append(self.request_handler.send_request(activity_dto))
        return responses

    def __get_post_info(self, in_reply_to_id, activity_dto):
        line = (in_reply_to_id).split("/")
        inbox_url = "/".join(line[:5]) + '/inbox'
        activity_dto.inbox_url = inbox_url
        activity_dto.domain = line[2]


