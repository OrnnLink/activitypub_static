import requests
import base64
import json
import hashlib
from datetime import datetime, timezone
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from modules.handler.base_handler import BaseHandler

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
        ...