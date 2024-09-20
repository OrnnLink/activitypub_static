+++
title = 'Signing Algorithm'
date = 2024-07-19T14:18:17+10:00
draft = false
 
[seeNext]
    signing_algorithm_refactor = "/extra/signing_algorithm_refactor"
+++

## Signing Algorithm {#Signing}

We will be implementing our private key signing algorithm using Python algorithm, it is recommended that you install the following python libraries on your machine or python environment:
```bash
pip install cryptography
pip install requests
```

{{< callout type="note" title="Note" >}}
Different ActivityPub platforms requires different levels of security for signature. The algorithm we used for this section have only been tested on Mastodon, Honk and Ktistec. It works successfully for both Mastodon and Honk, but Ktistec requires additional security that I haven't quite figured out yet due to resource constraint.
{{< /callout >}}

Here is the code for algorithm used for private key signing
```python
import requests
import json
import hashlib
import base64
import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key

class KeySigningHandler:
    def __init__(self, actorId, privateKeyPath):
        self.actorId = actorId 
        self.__initFollowUrl()
        self.privateKeyPath = privateKeyPath
        self.privateKey = self.__loadPrivateKey(privateKeyPath)
        
    def setPrivateKey(self, privateKeyPath: str):
        self.privateKeyPath = privateKeyPath
        self.privateKey = self.__loadPrivateKey(privateKeyPath)

    def setActorId(self, actorId):
        self.actorId = actorId 
        self.__initFollowUrl()

    def __initFollowUrl(self):
        cursor = actorId.split("/")
        self.followerUrl = "/".join(cursor[:len(cursor)-1]) + "followers"
        self.followingUrl = "/".join(cursor[:len(cursor)-1]) + "following"

    def __generateDigest(self, activity: str) -> str:
        sha256 = hashlib.sha256()
        sha256.update(activity.encode('utf-8'))
        digest = base64.b64encode(sha256.digest()).decode('utf-8')
        return f"SHA-256={digest}"

    def __loadPrivateKey(self, filePath: str):
        with open(filePath, "rb") as key_file:
            private_key = load_pem_private_key(key_file.read(), password=None)
        return private_key

    def __getActorObjUrl(self, username: str, domain: str) -> str:
        url = f"https://{domain}/.well-known/webfinger"
        params = { "resource": f"acct:{username}@{domain}"}
        response = requests.get(url, params=params)
        if response.ok:
            data = response.json()
            links = data.get("links", [])
            for link in links:
                if link.get("rel") == "self":
                    return link.get("href")
        return None

    def __getActorInboxUrl(self, actor_obj_url: str) -> str:
        headers = { "Accept": "application/activity+json"}
        response = requests.get(actor_obj_url, headers=headers)
        if response.ok:
            data = response.json()
            return data.get('inbox')
        return None

  

    def __gatherActorComponents(self, webfinger: str):
        try:
            username, domain = webfinger.split("@")[1:]
        except ValueError:
            return "Invalid Webfinger"
        
        actorObjUrl = self.__getActorObjUrl(username, domain)
        if not actorObjUrl:
            return "Invalid Webfinger"
        
        actorInboxUrl = self.__getActorInboxUrl(actorObjUrl)
        if not actorInboxUrl:
            return "Invalid Actor Object URL"
        
        inboxEndpoint = actorInboxUrl.split(f"https://{domain}")[1]
        return domain, actorObjUrl, actorInboxUrl, inboxEndpoint

    def __generateSignature(
        self, date: str, digest: str,
        activity: dict, 
        host: str,
        inboxEndpoint: str
    ) -> str:
        activity_json = json.dumps(activity)

        sign_string = f"(request-target): post {inboxEndpoint}\n"
        sign_string += f"host: {host}\n"
        sign_string += f"date: {date}\n"
        sign_string += f"digest: {digest}"

        signature = self.privateKey.sign(
            sign_string.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        signature_b64 = base64.b64encode(signature).decode("utf-8")
        key_id = f"{self.actorId}#main-key"
        signature_header = (
            f'keyId="{key_id}",'
            f'headers="(request-target) host date digest",'
            f'signature="{signature_b64}",'
            f'algorithm="rsa-sha256"'
        )
        return signature_header

    def generateSignedHeaders(self, activity: dict, targetWebfinger: str) -> dict:
        result = self.__gatherActorComponents(targetWebfinger)
        if isinstance(result, str):
            return {"error": result}

        domain, actorObjUrl, actorInboxUrl, inboxEndpoint = result
        date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        activity_json = json.dumps(activity)
        digest = self.__generateDigest(activity_json)
        signature = self.__generateSignature(date, digest, activity, domain, inboxEndpoint)
        
        headers = {
            "Host": domain,
            "Date": date,
            "Digest": digest,
            "Content-Type": "application/activity+json",
            "Signature": signature
        }
        return {
            "inbox_url": actorInboxUrl,
            "body": activity_json,
            "headers": headers
        }

    def generateFollowActivity(self, targetWebfinger):
        username, domain = targetWebfinger.split("@")[1:]
        actorObjUrl = self.__getActorObjUrl(username, domain)
        activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Follow",
            "actor": self.actorId,
            "object": actorObjUrl
        }
        return activity
    
    def generatePostActivity(self, postId, content, public=True):
        date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Create",
            "id": postId,
            "actor": self.actorId,
            "object": {
                "id": postId,
                "type": "Note", 
                "published": date,
                "content": content,
                "attributedTo": self.actorId,
                "to": [ self.followerUrl ],
                "cc": [ self.followerUrl]
            },
            "to": [ self.followerUrl ],
            "cc": [ self.followerUrl]
        }
        if public:
            publicFlag = "https://www.w3.org/ns/activitystreams#Public"
            activity["object"]['to'].append(publicFlag)
            activity['to'].append(publicFlag)
        return activity
```