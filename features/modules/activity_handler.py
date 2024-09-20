from modules.activity_request import *
from modules.activity_generator import ActivityGenerator

class ActivityHandler: 
    def __init__(self, actor_id, private_key_path):
        self.actor_id = actor_id
        self.generator = ActivityGenerator.get_instance()
        self.handler = ActivityPubRequestHandler(actor_id, private_key_path)
        
    def send_follow_activity(self, webfinger, debug=True):
        activity_dto = self.generator.generate_follow_activity(self.actor_id, webfinger)
        if isinstance(activity_dto, list):
            return activity_dto
        response = self.handler.send_request(activity_dto)
        return self.__interpret_response(activity='Follow', response=response, debug=debug)

    # def send_accept_activity(self, webfinger, debug=True):
    #     activity_dto = self.generator.generate_accept_activity(self.actor_id, webfinger)
    #     print(activity_dto.activity)
        # response = self.handler.send_request(activity_dto)
        # return self.__interpret_response(activity='Accept', response=response, debug=debug)
    
    def send_publish_activity(self, post_id, content, public=True, debug=True):
        activity_dto = self.generator.generate_publish_activity(self.actor_id, post_id, content, public)
        responses = self.__share_to_follower(activity_dto)
        return self.__interpret_response(activity='Publish', response=responses, debug=debug)
    
    # def send_delete_activity(self, post_id, debug=True):
    #     activity_dto = self.generator.generate_delete_activity(self.actor_id, post_id)
    #     responses = self.__share_to_follower(activity_dto)
    #     return self.__interpret_response(activity='Delete', response=responses, debug=debug)

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