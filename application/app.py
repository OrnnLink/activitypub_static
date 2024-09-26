from modules.generator.template.activity_template import ActivityTemplate
from modules.utility import extract_followers_inbox

template = ActivityTemplate("", "")
template.set_webfinger("@pbandj9819@mastodon.social")
# template.create()
# for s in (extract_followers_inbox("https://mastodon.social/users/pbandj9819/followers")):
#     print(s)