import unittest
import os
from tests.utility import make_test_folder, tear_down_test_folders, read_from_json
from modules.handler.user_data_handler import UserDataHandler

class UserDataHandlerTest(unittest.TestCase):
    def setUp(self):
        make_test_folder()
        self.handler = UserDataHandler()

    def tearDown(self):
        tear_down_test_folders() 
    
    def test_add_follower_with_no_id_and_no_webfinger(self):
        self.assertIsNone(self.handler.add_follower())
    
    def test_add_follower_with_actor_id(self):
        # Setting up
        username = 'noah'
        domain = 'staticap.netlify.app'
        actor_id = f"http://{domain}/users/{username}"
        path = f"tests/activitypub/static/{username}/user-info"
        self.handler.add_follower(actor_id)
        
        # Testing
        data = read_from_json(f"{path}/followers.json")
        self.assertEqual(1, data.get('totalItems'))
        data = read_from_json(f"{path}/followers/first.json")
        self.assertTrue(actor_id in data.get('orderedItems'))

    def test_add_follower_with_webfinger(self):
        # Setting up
        username = 'noah'
        domain = 'staticap.netlify.app'
        actor_id = f"https://{domain}/{username}/user-info/actor.json"
        webfinger = f"@{username}@{domain}"
        path = f"tests/activitypub/static/{username}/user-info"
        self.handler.add_follower(webfinger=webfinger)
        
        # Testing
        data = read_from_json(f"{path}/followers.json")
        self.assertEqual(1, data.get('totalItems'))
        data = read_from_json(f"{path}/followers/first.json")
        self.assertTrue(actor_id in data.get('orderedItems'))
    
    def test_remove_follower_with_webfinger(self):
        # Setting up
        username = 'noah'
        domain = 'staticap.netlify.app'
        webfinger = f"@{username}@{domain}"
        path = f"tests/activitypub/static/{username}/user-info"
        self.handler.add_follower(webfinger=webfinger)
        self.handler.remove_follower(webfinger=webfinger)
        
        # Testing
        data = read_from_json(f"{path}/followers.json")
        self.assertEqual(0, data.get('totalItems'))
        data = read_from_json(f"{path}/followers/first.json")
        self.assertTrue(len(data.get('orderedItems')) == 0)
    
    def test_remove_follower_with_actor_id(self):
        # Setting up
        username = 'noah'
        domain = 'staticap.netlify.app'
        actor_id = f"https://{domain}/{username}/user-info/actor.json"
        path = f"tests/activitypub/static/{username}/user-info"
        self.handler.add_follower(actor_id=actor_id)
        self.handler.remove_follower(actor_id=actor_id)
        
        # Testing
        data = read_from_json(f"{path}/followers.json")
        self.assertEqual(0, data.get('totalItems'))
        data = read_from_json(f"{path}/followers/first.json")
        self.assertTrue(len(data.get('orderedItems')) == 0) 
    
    def test_remove_follower_with_no_id_and_no_webfinger(self):
        self.assertIsNone(self.handler.remove_follower())
    
         
    # Following
    def test_add_following_with_no_id_and_no_webfinger(self):
        self.assertIsNone(self.handler.add_following())

    def test_add_following_with_actor_id(self):
        # Setting up
        username = 'noah'
        domain = 'staticap.netlify.app'
        actor_id = f"http://{domain}/users/{username}"
        path = f"tests/activitypub/static/{username}/user-info"
        self.handler.add_following(actor_id)
        
        # Testing
        data = read_from_json(f"{path}/following.json")
        self.assertEqual(1, data.get('totalItems'))
        data = read_from_json(f"{path}/following/first.json")
        self.assertTrue(actor_id in data.get('orderedItems'))

    def test_add_following_with_webfinger(self):
        # Setting up
        username = 'noah'
        domain = 'staticap.netlify.app'
        actor_id = f"https://{domain}/{username}/user-info/actor.json"
        webfinger = f"@{username}@{domain}"
        path = f"tests/activitypub/static/{username}/user-info"
        self.handler.add_following(webfinger=webfinger)
        
        # Testing
        data = read_from_json(f"{path}/following.json")
        self.assertEqual(1, data.get('totalItems'))
        data = read_from_json(f"{path}/following/first.json")
        self.assertTrue(actor_id in data.get('orderedItems'))
    
    def test_remove_following_with_webfinger(self):
        # Setting up
        username = 'noah'
        domain = 'staticap.netlify.app'
        webfinger = f"@{username}@{domain}"
        path = f"tests/activitypub/static/{username}/user-info"
        self.handler.add_following(webfinger=webfinger)
        self.handler.remove_following(webfinger=webfinger)
        
        # Testing
        data = read_from_json(f"{path}/following.json")
        self.assertEqual(0, data.get('totalItems'))
        data = read_from_json(f"{path}/following/first.json")
        self.assertTrue(len(data.get('orderedItems')) == 0)
    
    def test_remove_following_with_actor_id(self):
        # Setting up
        username = 'noah'
        domain = 'staticap.netlify.app'
        actor_id = f"https://{domain}/{username}/user-info/actor.json"
        path = f"tests/activitypub/static/{username}/user-info"
        self.handler.add_following(actor_id=actor_id)
        self.handler.remove_following(actor_id=actor_id)
        
        # Testing
        data = read_from_json(f"{path}/following.json")
        self.assertEqual(0, data.get('totalItems'))
        data = read_from_json(f"{path}/following/first.json")
        self.assertTrue(len(data.get('orderedItems')) == 0)  

    def test_remove_following_with_no_id_and_no_webfinger(self):
        self.assertIsNone(self.handler.remove_following())
    
    # Publish
    def test_publish_post(self):
        url = "statuses"
        title = "test"
        content = "testing"
        public = True
        update = False
        self.handler.publish_post(url, title, content, public, update)
        self.assertTrue(os.path.isfile(f"tests/activitypub/content/noah/{url}/{title}.md"))

        filename = f"tests/activitypub/static/noah/content/{url}/{title}.json"
        self.assertTrue(os.path.isfile(filename))
        
    def test_update_post(self):
        url = "statuses"
        title = "test"
        content = "testing"
        public = True
        update = False
        content = "wow"
        self.handler.publish_post(url, title, content, public, update)
        self.handler.publish_post(url, title, content, public, update=True)

        self.assertTrue(os.path.isfile(f"tests/activitypub/content/noah/{url}/{title}.md"))
        filename = f"tests/activitypub/static/noah/content/{url}/{title}.json"
        data = read_from_json(filename)
        self.assertEqual(content, data.get('object').get('content'))
     
    # Reply
    def test_add_reply(self): 
        title = "reply"
        in_reply_to_id = "in_reply_to_id"
        content = "reply"
        self.handler.add_reply(title, in_reply_to_id, content)
        self.assertTrue(os.path.isfile(f"tests/activitypub/static/noah/replies/{title}.json"))


        
        
        
        
    