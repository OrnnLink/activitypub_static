+++
title = 'Publish Post Feature'
date = 2024-08-09T15:34:24+10:00
draft = false
+++

For a post to be visible on another user's instance, a relationship between your static site actor and the other actor is essential. Specifically, you must either follow the other user or have received a follow request from them that you accepted.

Assuming these conditions are met, you can create a post and share it with your followers or those you follow.

### Example: Simple Python Program to Follow

```python
# Assuming the following algorithm is in KeySigningHandler.py in the same directory
import requests
from ActivityHandler import *

# URL pointing to your actor object
actor_id = "https://noah.netlify.app/noah/actor.json"

# Path to the private key generated using the "Webfinger for Discovery Post" algorithm
private_key_path = "..."

# Webfinger of the user you want to follow
webfinger = "@alice@mastodon.social"

# Activity Information
# Store the post ID uniquely; in this case, it's the URL of the post
post_id = "https://noah.netlify.app/posts/first"
content = "example content"

# Flag indicating whether the post is public or private
public = True

handler = ActivityHandler(actor_id, private_key_path)
handler.send_publish_activity(
    post_id=post_id,
    content=content,
    public=public
)
```

**Requirements:**

1. URL pointing to your actor object.
2. A brief description for the post you are sharing.
3. The ID assigned to the post (can be a URL to the post or the post object itself).
4. Webfinger of the user you follow or who has followed you.

**Structure of a `@Create` Activity:**

```json
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
            "https://www.w3.org/ns/activitystreams#Public"  // Includes this if public
        ],
        "cc": [ "{YOUR_ACTOR_FOLLOWERS_URL}" ]
    },
    "published": "...",
    "to": [ 
        "{YOUR_ACTOR_FOLLOWERS_URL}",
        "https://www.w3.org/ns/activitystreams#Public"  // Includes this if public
    ],
    "cc": [ "{YOUR_ACTOR_FOLLOWERS_URL}" ]
}
```
---

**References**
- [Adding ActivityPub to Your Static Site - Paul Kinlan](https://paul.kinlan.me/adding-activity-pub-to-your-static-site/)
- [Create Activity](https://www.w3.org/TR/activitypub/#create-activity-outbox)

---

**See also**
- [Running ActivityPub Server on Static Site](/page/running_activitypub_server_leveraging_static_web_hosting/)
- [Getting Follow Feature](/page/extra/getting_follow_feature)
- [Following Feature](/page/extra/follow_feature)
- [Codebase](/page/extra/activitypub_codebase)




