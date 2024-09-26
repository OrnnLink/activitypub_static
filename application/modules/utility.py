import requests

def send_get_request(url, headers={}, params={}):
    if headers == {}:
        headers = { "accept": "application/activity+json"}
    return requests.get(url, headers=headers, params=params)

def extract_username_and_domain(webfinger):
    return webfinger.split("@")[1:]