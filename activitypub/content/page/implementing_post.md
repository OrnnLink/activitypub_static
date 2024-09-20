+++
title = 'Implementing Post'
date = 2024-07-19T13:49:52+10:00
draft = false
tags = [ "Static-Site", "ActivityPub" ]
summary = """
Following up on "Implementing Follow", this article offers and extension for implementing a post publishing feature, that allows you to share contents with a list of your following users on different ActivityPub instances
"""

[prerequisites]
	signing_algorithms = "/extra/signing_algorithm"
	implementing_follow = "/page/implementing_follow"

+++


For a post to be visible on another user instance, it's important that there exists a relationship between your static site actor and another actor on different instance. i.e. You must at least follow another user, or another user has requested to followed your static site actor, and you have sent an "Accept" activity back to that actor. 

Assuming the above requirements are met, we can make a posts and share it to our follower/following.

Example - a simple python program used to followed
```python
# Assuming the above algorithm is stored under KeySigningHandler.py
# under the same directory
import requests
from KeySigningHandler import *


# This is the url that leads to your actor object
actorId = "https://noah.netlify.app/noah/actor.json"

# This is the file path leading to the private key generated 
# using the algorithm found in "Webfinger for Discovery Post"
privateKeyPath = "..."

# This is the webfinger of the user that you want to follow
webfinger = "@alice@mastodon.social"

# Activity Information
# You can use anyway of storing post id, as long as they are unique
# In our case, we just use the url of the post 
postId = "https://noah.netlify.app/posts/first"
content = "exmaple content"

# Flag that determines whether or not the post is public or private
public = True

handler = KeySigningHandler(actorId, privateKeyPath)
activity = handler.generatePostActivity(postId, content)
inboxUrl, body, headers = handler.generateSignedHeaders(webfinger)

response = requests.post(inboxUrl, headers=headers, data=data)
if response.ok:
	print(f"Successfully followed: {webfinger}")
else:
	print(f"{response.status_code}: Unable to follow {webfinger}")
	print(response.reason)
```

**Quick Summary of the Above Code:** 

Things you need:

1. {{< pretty-code >}}URL{{< /pretty-code >}} that leads to your actor Object
2. a short description used as {{< pretty-code >}}content{{< /pretty-code >}} for the post you are sharing
3. the {{< pretty-code >}}ID{{< /pretty-code >}} assigned to the post, this can be in form of url that leads to post html display, or the post object. 
4. {{< pretty-code >}}Webfinger{{< /pretty-code >}} of the person you followed, or has followed you
 
Process:
1. Initialise the {{< pretty-code >}}KeySigningHandler{{< /pretty-code >}} object, using the actor object url and path to your private key
2. Generate the [@Create](https://www.w3.org/TR/activitypub/#create-activity-outbox) activity using the {{< pretty-code >}}generatePostActivity(postId, content, public){{< /pretty-code >}}, with the 3 parameters respectively. By default, the value of public is true, meaning when you publish a post, it can be seen by anyone after you shared them
3. Calls the {{< pretty-code >}}generateSignedHeader{{< /pretty-code >}} method using the previously generated activity nd target user webfinger. This would return the `(inboxUrl, body, headers)`. Each of the components can be explained as followed:
	1. `inboxUrl` - the url that we needs to send the returned `body` and `header` to
	2. `body` - the json version of the activity that was previously generated in step 2
	3. `headers` - formatted headers with necessarily information to meet the ActivityPub protocol requirements
4. Using the returned values from step 3, we make a POST HTTP request to `inboxUrl` using the `body` and `headers` 

The structure of a [@Create](https://www.w3.org/TR/activitypub/#create-activity-outbox) activity is typically created as followed:
```python
{
	"@context": "https://www.w3.org/ns/activitystreams",
	"type": "Create",
	"id": "{ID_OF_YOUR_POST}", 
	"actor": "{YOUR_ACTOR_OBJECT_URL}", 
	"object": {
		"id": "{ID_OF_YOUR_POST}",
		"type": "Note",
		"attributedTo": "{YOUR_ACTOR_OBJECT_URL}",
		"content": "{CONTENT}",
		"to": [ 
			"{YOUR_ACTOR_FOLLOWERS_URL}",
			# Includes the following if public
			"https://www.w3.org/ns/activitystreams#Public"
		],
		"cc": [ "{YOUR_ACTOR_FOLLOWERS_URL}"]
	},
	"published": "...",
	"to": [ 
		"{YOUR_ACTOR_FOLLOWERS_URL}",
		# Includes the following if public
		"https://www.w3.org/ns/activitystreams#Public"
	],
	"cc": [ "{YOUR_ACTOR_FOLLOWERS_URL}"]
}
```


---
**References**
- [Adding ActivityPub to Your Static Site - Paul Kinlan](https://paul.kinlan.me/adding-activity-pub-to-your-static-site/)
- [Create Activity - W3.org](https://www.w3.org/TR/activitypub/#create-activity-outbox)