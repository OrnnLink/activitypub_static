from modules.generator.template.activity_template import ActivityTemplate
from modules.generator.template.publish_activity_template import *
from modules.generator.template.follow_activity_template import *

template = FollowActivityTemplate("", "https://mastodon.social/users/pbandj9819/followers")
data = {
    "post_id": "post id",
    "content": "post content",
    "public": True,
    "webfinger": "@pbandj9819@mastodon.social"
}
print(template.create(data))
# template.create()
# for s in (extract_followers_inbox("https://mastodon.social/users/pbandj9819/followers")):
#     print(s)