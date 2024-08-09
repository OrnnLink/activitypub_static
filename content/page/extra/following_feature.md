+++
title = 'Following Feature'
date = 2024-08-09T15:09:44+10:00
draft = false
+++

Before implementing these features, you need to set up your WebFinger and actor object. Additionally, you must implement the required handler objects. For simplicity, we’ll use Python for this implementation. Once you have both the WebFinger and handler objects set up, you can use the following example to send a follow request to another user on ActivityPub instances.

### Example: Simple Python Program to Send a Follow Request

```python
# Assuming the signing algorithm is implemented in KeySigningHandler.py in the same directory
import requests
from ActivityHandler import *

# URL pointing to your actor object
actor_id = "https://noah.netlify.app/noah/actor.json"

# Path to the private key generated using the signing algorithm
private_key_path = "..."

# WebFinger of the user you want to follow
webfinger = "@alice@mastodon.social"

handler = ActivityHandler(actor_id, private_key_path)
handler.send_follow_activity(webfinger=webfinger)
```
**Requirements:**

1. URL pointing to your actor object.
2. WebFinger of the person you want to follow.

**Structure of a `@Follow` Activity:**

```json
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
- [Follow Activity](https://www.w3.org/TR/activitypub/#follow-activity-outbox)

---

**See also**
- [Running ActivityPub Server on Static Site](/activitypub_static/page/running_activitypub_server_leveraging_static_web_hosting/)
- [Codebase](/activitypub_static/page/extra/activitypub_codebase)
