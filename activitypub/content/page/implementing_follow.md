+++
title = 'Implementing Follow'
date = 2024-07-19T13:49:43+10:00
draft = false
tags = [ "Static Site", "ActivityPub" ]
summary = """
Following up on "Webfinger for Discovery", this article offers an extension to implementing a following feature, where a user from your static site can send a follow request to other users on various ActivityPub instances, such that you can share your contents to those you are followings.
"""
[seeNext]
	implementing_post = "/page/implementing_post"
[prerequisites]
	signing_algorithm = "/extra/signing_algorithm"
	webfinger = "/page/webfinger_for_discovery"
+++

It's a requirements for you to setup your webfinger and actor object prior to implementing this features. You would also need to implement the following [Signing Algorithm](https://sdlay.netlify.app/extra/signing_algorithm) (for simplicity, we'll implement it in Python). After implemented both the webfinger and key signing algorithm, you can use the below example to send a follow request to someone on ActivityPub instances. 

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

handler = KeySigningHandler(actorId, privateKeyPath)
activity = handler.generateFollowActivity(webfinger)
inboxUrl, body, headers = handler.generateSignedHeaders(activity, webfinger)

response = requests.post(inboxUrl, headers=headers, data=data)
if response.ok:
	print(f"Successfully followed: {webfinger}")
else:
	print(f"{response.status_code}: Unable to follow {webfinger}")
	print(response.reason)
```

**Quick Summary of the Above Code:** 

Things you need:

1. URL that leads to your actor Object
2. The person you want to follow Webfinger 

Process:
1. Initialise the {{< pretty-code >}}KeySigningHandler{{< /pretty-code >}} object, using the actor object url and path to your private key
2. Generate the [@Follow](https://www.w3.org/TR/activitypub/#follow-activity-outbox) activity using the target user webfinger
3. Calls the {{< pretty-code >}}generateSignedHeader{{< /pretty-code >}} method using the previously generated activity and target user webfinger. This would return the `(inboxUrl, body, headers)`. Each of the components can be explained as followed:
	3.1. `inboxUrl` - the url that we needs to send the returned `body` and `header` to
	3.2. `body` - the json version of the activity that was previously generated in step 2
	3.3. `headers` - formatted headers with necessarily information to meet the ActivityPub protocol requirements
4. Using the returned values from step 3, we make a POST HTTP request to `inboxUrl` using the `body` and `headers`

The structure of a [@Follow](https://www.w3.org/TR/activitypub/#follow-activity-outbox) activity is as followed:
```python
{
	"@context": "https://www.w3.org/ns/activitystreams",
	"type": "Follow",
	"actor": "{YOUR_ACTOR_OBJECT_URL}", 
	"object": "{TARGET_ACTOR_OBJECT_URL}"
}
```

---
**References**
- [Adding ActivityPub to Your Static Site - Paul Kinlan](https://paul.kinlan.me/adding-activity-pub-to-your-static-site/)
- [Follow Activity - w3 org](https://www.w3.org/TR/activitypub/#follow-activity-outbox)

