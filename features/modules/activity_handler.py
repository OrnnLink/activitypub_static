import json
from modules.activity_request import *
from modules.activity_generator import ActivityGenerator

class ActivityHandler: 
    def __init__(self):
        self.__load_config()

    def __load_config(self):
        filename = "config.json"
        with open(filename, "r") as fd:
            data = json.load(fd)
        self.username = data['username']
        self.domain= data['domain']
        private_key_path = data["private_key_path"]
        self.actor_id = f"https://{self.domain}/{self.username}/user-info/actor.json"
        self.generator = ActivityGenerator.get_instance()
        self.handler = ActivityPubRequestHandler(self.actor_id, private_key_path)

    def send_follow_activity(self, webfinger, debug=True):
        activity_dto = self.generator.generate_follow_activity(self.actor_id, webfinger)
        if isinstance(activity_dto, list):
            return activity_dto
        response = self.handler.send_request(activity_dto)
        return self.__interpret_response(activity='Follow', response=response, debug=debug)

    def send_publish_activity(self, post_id, content, public=True, debug=True):
        activity_dto = self.generator.generate_publish_activity(self.actor_id, post_id, content, public)
        responses = self.__share_to_follower(activity_dto)
        return self.__interpret_response(activity='Publish', response=responses, debug=debug)
    
    def __share_to_follower(self, activity_dto):
        responses = []
        for follower in activity_dto.followers:
            domain, inbox_url, inbox_endpoint = follower
            activity_dto.domain = domain
            activity_dto.inbox_url = inbox_url
            activity_dto.inbox_endpoint = inbox_endpoint
            responses.append(self.handler.send_request(activity_dto))
        return responses

    def __interpret_response(self, activity, response, debug=True):
        if not debug:
            return response
        if activity in ["Follow", "Accept"]:
            if response.ok:
                print(f'\n{activity} activity successfully operated!\n')
                print(response.text)
            else:
                print(f'\nUnsuccessful {activity} activity')
                print(f'Status code: {response.status_code}')
                print(f'Reason: {response.reason}')
            return response
        
        success = 0
        failure = 0
        for item in response:
            if item.ok:
                success += 1
                print(f'\n{activity} activity successfully operated!\n')
                print(item.text)
            else:
                failure += 1
                print(f'\nUnsuccessful {activity} activity')
                print(f'Status code: {item.status_code}')
                print(f'Reason: {item.reason}')
                print(item.text)
            
        total = success + failure
        print(f"\nOverall")
        print(f"Success: {success}")
        print(f"Failure: {failure}")
        print(f"Total: {total}")
        return response
