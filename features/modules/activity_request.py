import requests
import base64
import json
import hashlib
from datetime import datetime, timezone
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

class ActivityPubRequestHandler:
    def __init__(self, actor_id, private_key_path):
        self.actor_id = actor_id
        self.private_key_path = private_key_path
        self.private_key = self.__load_private_key()

    def __load_private_key(self) -> None:
        with open(self.private_key_path, "rb") as key_file:
            private_key = load_pem_private_key(key_file.read(), password=None)
        return private_key

    def send_request(self, activity_dto):
        # Gather information
        domain = activity_dto.domain
        inbox_url = activity_dto.inbox_url
        inbox_endpoint = activity_dto.inbox_endpoint
        activity = activity_dto.activity

        # Convert Activity to JSON 
        activity = json.dumps(activity)
        
        # Generates Headers
        headers = self.__generate_headers(domain, activity, inbox_endpoint)
       
        return self.__send_post_request(inbox_url, headers, activity)
    
    # Support functions for send_activity
    def __generate_headers(self, domain, activity, inbox_endpoint): 
        headers = { "Content-Type": "application/activity+json"}
    
        headers['Host'] = domain

        date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        headers['Date'] = date

        digest = self.__generate_digest(activity)
        headers['Digest'] = digest
         
        headers['Signature'] = self.__generate_signature(headers, inbox_endpoint)
        return headers

    def __generate_digest(self, activity: str) -> str:
        sha256 = hashlib.sha256()
        sha256.update(activity.encode('utf-8'))
        digest = base64.b64encode(sha256.digest()).decode('utf-8')
        return f"SHA-256={digest}"
        
    def __generate_signature(self, headers, inbox_endpoint):
        sign_string = f'(request-target): post {inbox_endpoint}\n'
        sign_string += f'host: {headers["Host"]}\n'
        sign_string += f'date: {headers["Date"]}\n'
        sign_string += f'digest: {headers["Digest"]}'
        
        signature = self.private_key.sign(
            sign_string.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        signature = base64.b64encode(signature).decode('utf-8')

        key_id = f"{self.actor_id}#main-key"
        signature_header = (
        f'keyId="{key_id}",'
        f'headers="(request-target) host date digest",'
        f'signature="{signature}",'
        f'algorithm="rsa-sha256"'
        )
        
        return signature_header

    def __send_post_request(self, url, headers, activity):
        return requests.post(url, headers=headers, data=activity)