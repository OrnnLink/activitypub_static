import unittest
from tests.utility import make_test_folder, tear_down_test_folders
from modules.dto.activity_dto import ActivityDTO
from modules.generator.activity_generator import ActivityGenerator
from modules.handler.config_data_handler import ConfigDataHandler

class ActivityGeneratorTest(unittest.TestCase): 
    def setUp(self): 
        self.generator = ActivityGenerator.get_instance()
        make_test_folder()

    def tearDown(self):
        tear_down_test_folders()

    def test_generate_follow_activity(self):
        actor_id = "http://test.example.com/users/testuser"
        webfinger = '@pbandj9819@mastodon.social'
        dto = ActivityDTO(webfinger=webfinger)
        activity = self.generator.generate_follow_activity(actor_id, dto)
        expected = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Follow",
            "actor": actor_id,
            "object": "https://mastodon.social/users/pbandj9819"
        }
        self.assertEqual(expected, activity)
        
    def test_generate_publish_activity(self):
        actor_id = "http://test.example.com/users/testuser"
        post_id = "post_id"
        content = "content"
        ins = ConfigDataHandler.get_instance()
        dto = ActivityDTO(
            post_id=post_id, content=content, public=True,
            follower_url=ins.follower_url, username=ins.username
        )
        activity = self.generator.generate_publish_activity(actor_id, dto)
        expected = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Create",
            "id": post_id,
            "actor": actor_id,
            "object": {
                "id": post_id.replace(f"page/{ins.username}", f"{ins.username}/content"),
                "type": "Note", 
                "content": content,
                "attributedTo": actor_id,
                "to": [ ins.follower_url, "https://www.w3.org/ns/activitystreams#Public"],
                "cc": [ ins.follower_url]
            },
            "to": [ ins.follower_url, "https://www.w3.org/ns/activitystreams#Public"],
            "cc": [ ins.follower_url]
        }
        for key in expected:
            if key != "object":
                self.assertEqual(expected[key], activity[key])
        for key in expected['object']:
            if key != "published":
                self.assertEqual(expected['object'][key], activity['object'][key])
        
    def test_generate_unfollow_activity(self):
        actor_id = "http://test.example.com/users/testuser"
        webfinger = '@pbandj9819@mastodon.social'
        dto = ActivityDTO(webfinger=webfinger)
        activity = self.generator.generate_unfollow_activity(actor_id, dto)
        expected = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Undo",
            "object": {
                "type": "Follow",
                "actor": actor_id,
                "object": "https://mastodon.social/users/pbandj9819"
            }
        }
        self.assertEqual(expected, activity)
        
    def test_generate_update_activity(self):
        actor_id = "http://test.example.com/users/testuser"
        post_id = "post_id"
        content = "content"
        ins = ConfigDataHandler.get_instance()
        dto = ActivityDTO(
            post_id=post_id, content=content, public=True,
            follower_url=ins.follower_url, username=ins.username
        )
        activity = self.generator.generate_update_activity(actor_id, dto)
        expected = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Update",
            "actor": actor_id,
            "object": {
                "id": post_id.replace(f"page/{ins.username}", f"{ins.username}/content"),
                "type": "Note", 
                "content": content,
                "attributedTo": actor_id,
                "to": [ ins.follower_url, "https://www.w3.org/ns/activitystreams#Public"],
            },
            "to": [ ins.follower_url, "https://www.w3.org/ns/activitystreams#Public"],
        }
        for key in expected:
            if key != "object":
                self.assertEqual(expected[key], activity[key])
        for key in expected['object']:
            if key != "updated": 
                self.assertEqual(expected['object'][key], activity['object'][key])

    def test_generate_reply_activity(self):
        actor_id = "http://test.example.com/users/testuser"
        post_id = "post_id"
        content = "content"
        in_reply_to_id="in_reply_to_id "
        dto = ActivityDTO(
            post_id=post_id, content=content, in_reply_to_id=in_reply_to_id
        )
        activity = self.generator.generate_reply_activity(actor_id, dto)
        expected = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Create",
            "id": post_id,
            "actor": actor_id,
            "object": {
                "id": post_id,
                "type": "Note", 
                "content": content,
                "inReplyTo": in_reply_to_id
            },
        } 
        for key in expected:
            if key != "object":
                self.assertEqual(expected[key], activity[key])
        for key in expected['object']:
            if key != "published":
                self.assertEqual(expected['object'][key], activity['object'][key])