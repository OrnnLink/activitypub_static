import unittest

from modules.activity_handler import *

class FollowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.handler = ActivityHandler()
        cls.actor_id = cls.handler.actor_id
        
    # def test_follow_non_existing_honk_user(self):
    #     webfinger = "@noah1@daniellay.cc"
    #     value = self.handler.send_follow_activity(webfinger, debug=False)
    #     self.assertTrue(isinstance(value, list))
    #     self.assertEqual("Unable to retrieve actor object: Not Found", value[0]) 
    #     self.assertEqual("Unknown actor object", value[1]) 

    # def test_follow_existing_honk_user(self):
    #     webfinger = "@noah@daniellay.cc"
    #     value = self.handler.send_follow_activity(webfinger,debug=False)
    #     self.assertEqual(200, value.status_code)

    # def test_follow_already_followed_honk_user(self):
    #     webfinger = "@noah@daniellay.cc"
    #     value = self.handler.send_follow_activity(webfinger,debug=False)
    #     self.assertEqual(200, value.status_code)

    def test_follow_existing_mastodon_user(self):
        webfinger = "@pbandj9819@mastodon.social"
        value = self.handler.send_follow_activity(webfinger,debug=False)
        self.assertEqual(202, value.status_code)

    def test_follow_non_existing_mastodon_user(self):
        webfinger = "@non_existing_user_404@mastodon.social"
        value = self.handler.send_follow_activity(webfinger,debug=False)
        self.assertTrue(isinstance(value, list))
        self.assertEqual("Unable to retrieve actor object: Not Found", value[0]) 
        self.assertEqual("Unknown actor object", value[1]) 

if __name__ == '__main__':
    unittest.main()
