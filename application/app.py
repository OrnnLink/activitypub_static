from modules.controller.activity_controller import ActivityController
from modules.handler.get_reply_handler import GetReplyHandler
controller = ActivityController()
# controller.send_follow_activity()
# controller.send_unfollow_activity()
# controller.update_followers()
# controller.publish_content()
# controller.create_user()

g = GetReplyHandler()
g.get_replies()
