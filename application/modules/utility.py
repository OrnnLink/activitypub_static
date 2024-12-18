import json
import os
import requests
from modules.dto.activity_dto import ActivityDTO

def send_get_request(url, headers={}, params={}):
    if headers == {}:
        headers = { "accept": "application/activity+json"}
    try:
        return requests.get(url, headers=headers, params=params)
    except Exception:
        return None

def send_post_request(url, headers, activity):
    return requests.post(url, headers=headers, data=activity)

def read_from_json(filename):
    try:
        with open(filename, "r") as fd:
            return json.load(fd)
    except Exception as e:
        return None

def write_to_json(data: dict, filename: str):
    with open(filename, "w") as fd:
        try:
            fd.write(json.dumps(data, indent=4))
        except Exception:
            return False
    return True

def make_directory(name: str):
    if not os.path.isdir(name):
        os.makedirs(name)
        return True
    return False

def extract_username_and_domain(webfinger):
    return webfinger.split("@")[1:]

def extract_followers_inbox(follower_url):
    if follower_url == None:
        return None
    follower_ids = __get_follower_ids(follower_url)
    inboxes = __get_inbox_urls(follower_ids)
    for i in range(len(inboxes)):
        data = inboxes[i].split("/")
        domain = data[2]
        inboxes[i] = ActivityDTO(domain=domain, inbox_url=inboxes[i])
    return inboxes

def extract_followers_outbox(follower_url):
    if follower_url == None:
        return None
    follower_ids = __get_follower_ids(follower_url)
    outboxes = __get_outbox_urls(follower_ids)
    for i in range(len(outboxes)):
        data = outboxes[i].split("/")
        domain = data[2]
        outboxes[i] = ActivityDTO(domain=domain, outbox_url=outboxes[i])
    return outboxes

def __get_follower_ids(follower_url):
    response = send_get_request(follower_url)
    data = json.loads(response.text)

    if "orderedItems" in data:
        return __get_follower_id_from_ordered_items(data)
    return __get_follower_id_from_ext_url(data)

def __get_follower_id_from_ordered_items(data):
    items = data["orderedItems"]
    ids = []
    for item in items:
        if type(item) == str:
            ids.append(item)
        elif type(item) == dict:
            ids.append(item['id'])
    return items

def __get_follower_id_from_ext_url(data):
    excluded_keys = [ "@context", "id", "type", "totalItems"]
    urls = []
    # Getting relevant urls
    for key in data:
        if key not in excluded_keys:
            urls.append(data[key])

    total = data['totalItems']
    follower_ids = []
    while True:
        url = urls.pop(0)
        response = requests.get(url, headers={ "accept": "application/activity+json"})
        json_data = json.loads(response.text)

        if "orderedItems" not in json_data.keys():
            break

        for item in json_data['orderedItems']:
            if type(item) == str:
                follower_ids.append(item)
            elif type(item) == dict:
                follower_ids.append(item['id'])

        if len(follower_ids) >= total:
            break

        # Registered the next urls
        if "next" in json_data.keys():
            urls.append(json_data["next"])
        elif "last" in json_data.keys():
            urls.append(json_data["last"])
        else:
            break
    return follower_ids

def __get_inbox_urls(follower_ids):
    inboxes = []
    for id in follower_ids:
        if isinstance(id, str):
            response = send_get_request(id)
            if response is None or not response.ok:
                continue

            data = json.loads(response.text)
            inboxes.append(data['inbox'])
        elif isinstance(id, dict):
            inboxes.append(id['inbox'])

    return inboxes

def __get_outbox_urls(follower_ids):
    outboxes = []
    for id in follower_ids:
        if isinstance(id, str):
            response = send_get_request(id)
            if response is None or not response.ok:
                continue

            data = json.loads(response.text)
            outboxes.append(data['outbox'])
        elif isinstance(id, dict):
            outboxes.append(id['outbox'])
    return outboxes
