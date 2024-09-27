import base64
import json
import hashlib
from datetime import datetime, timezone
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from modules.handler.base_handler import BaseHandler
from modules.utility import send_post_request

class ActivityRequestHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.__load_private_key()
    
    def __load_private_key(self): 
        with open(self.private_key_path, "rb") as fd:
            self.private_key = load_pem_private_key(fd.read(), password=None)

    def send_request(self, activity_dto):
        domain = activity_dto.domain
        inbox_url = activity_dto.inbox_url
        inbox_endpoint = activity_dto.get_inbox_endpoint()
        activity = json.dumps(activity_dto.activity)

        headers = self.__generate_headers(domain, activity, inbox_endpoint)
        return send_post_request(inbox_url, headers, activity)

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