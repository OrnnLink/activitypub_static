from modules.utility import read_from_json
from modules.controller.activity_controller import ActivityController
import subprocess


# g = GetReplyHandler()
# g.get_replies()
activity_files = {
	1: "following_activity.json",
	2: "unfollow_activity.json",
	4: "reply_to_post_activity.json",
	5: "webfinger_activity.json",
	6: "update_followers_activity.json",
	7: "publish_activity.json"
}

for key in activity_files:
	activity_files[key] = f"activities/{activity_files[key]}"
msg = """
Welcome to you Static Site ActivityPub Application! What would you like to do today?
[1] - Sending out a **FOLLOW** request
[2] - Sending out an **UN-FOLLOW** request
[3] - Seeing a list of **REPLIES** from your posts within 3 months
[4] - Sending out a **REPLY** to post
[5] - Create new **USER**
[6] - Update your **FOLLOWERS** list
[7] - Publish new **CONTENT** 
"""

def get_user_input():
	global msg
	global activity_files
	print(msg)
	user_input = input("Enter your input [1->6]: ")
	try:
		user_input = int(user_input)
	except ValueError:
		print('\nPlease enter a number!')
		return get_user_input()
	if user_input <= 0 or user_input >= 8:
		print("\nPlease enter a number between 1 -> 7")
		return get_user_input()

	if user_input == 3:
		print('\nYou have selected to see a list of replies')
		return 3
	print("\nPlease verify that the following information is correct!")
	data = read_from_json(activity_files[user_input])
	print(data)
	verify = input("\nIs the information correct? [Y|N] ").lower()
	if verify == "Y":
		return user_input
	else:
		return None

def main():
	controller = ActivityController()
	user_input = get_user_input()
	if user_input == None:
		print("\nExiting the program .....")
		return

	if user_input == 1:
		controller.send_follow_activity()
	elif user_input == 2:
		controller.send_unfollow_activity()
	elif user_input == 3:
		controller.get_replies()
	elif user_input == 4:
		controller.send_reply()
	elif user_input == 5:
		controller.create_user()
	elif user_input == 6:
		controller.update_followers()
	elif user_input == 7:
		controller.publish_content()

	site_dir_path = controller.handler['activity'].site_dir_path
	if user_input != 3:
		command = f"cd {site_dir_path} && hugo"
		subprocess.run(command, shell=True, capture_output=True, text=True)


if __name__ == "__main__":
	controller = ActivityController()
	# controller.send_reply()
	# controller.get_replies()
	# controller.send_follow_activity()
	# controller.send_unfollow_activity()
	# controller.update_followers()
	# controller.publish_content()
	# controller.create_user()
	...

	# main()

