import unittest

from modules.activity_handler import ActivityHandler

class PublishTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.handler = ActivityHandler(cls.actor_id, cls.private_key_path)
        cls.actor_id = cls.handler.actor_id
        cls.data = {
            "post_id": f"https://{self.handler.domain}/{self.handler.username}/post-json/spring.json",
            "content": "<p>Spring is coming</p>",
            "public": True
        }

    def __verify_basic_response(self, response):
        self.assertTrue(
            response.status_code >= 200 and response.status_code < 300
        )
        self.assertTrue(len(response.text) == 0)
        
    def test_publish_new_public_post(self):
        post_id, content, public = self.data.values()
        responses = self.handler.send_publish_activity(post_id, content, public, debug=False)
        for response in responses:
            self.__verify_basic_response(response)
        

