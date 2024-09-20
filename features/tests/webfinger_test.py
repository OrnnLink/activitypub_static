from .utility import get_mastodon_token
import unittest
import requests
import json

"""
Some Abbreviations: 
- SS: Static Site
- pf: Profile 
"""
class StaticSiteWebfingerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ... 
        
    def test_lookup_existing_SS_pf_on_mastodon(self):
        url = "https://mastodon.social/api/v2/search"
        headers = { "Authorization": f"Bearer {get_mastodon_token()}"}
        params = {
            "q": "@ylay@sdlay.netlify.app"
        }
        response = requests.get(url, headers=headers, params=params)
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.text)
        
        json_data = json.loads(response.text)
        self.assertTrue(len(json_data['accounts']) > 0)
        
    def test_lookup_non_existing_SS_pf_on_mastodon(self):
        url = "https://mastodon.social/api/v2/search"
        headers = { "Authorization": f"Bearer {get_mastodon_token()}"}
        params = {
            "q": "@noah@sdlay.netlify.app"
        }
        response = requests.get(url, headers=headers, params=params)
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.text)
        
        json_data = json.loads(response.text)
        self.assertTrue(len(json_data['accounts']) == 0)
