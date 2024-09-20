import unittest

# Now you can import `activity_handler`
from modules.get_reply import *

class FollowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actor_id = "https://sdlay.netlify.app/user-info/ylay/actor.json" 
        cls.webfinger = "@ylay@sdlay.netlify.app"
        cls.handler = PostReplyHandler(cls.actor_id, cls.webfinger, single_user=True)   

    def __get_complex_handler(self):
        actor_id = "https://mastodon.social/users/pbandj9819" 
        webfinger = "@pbandj9819@mastodon.social"
        handler = PostReplyHandler(actor_id, webfinger, single_user=False)   
        return handler 

    def test_basic_get_replies(self):
        self.handler.actor_id = "https://sdlay.netlify.app/user-info/ylay/actor.json" 
        self.handler.webfinger = "@ylay@sdlay.netlify.app"
        replies = self.handler.get_replies() 
        self.assertEqual(1, len(replies))
    
    def test_complex_get_replies(self):
        self.handler = self.__get_complex_handler()
        replies = self.handler.get_replies()
        self.assertEqual(5, len(replies))
