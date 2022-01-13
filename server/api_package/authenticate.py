import M2Crypto
import base64
from flask import g, request

class SessionKeyAuthenticator(object):

    def __init__(self, db):
        super().__init__()
        self.db = db

    def generate_session_key(self):
        key = base64.b64encode(M2Crypto.m2.rand_bytes(16))
        while self.db.is_session_key_in_db(key):
            key = base64.b64encode(M2Crypto.m2.rand_bytes(16))
        self.db.insert_session_key(key)
        return key

    def generate_authenticator(self):
        # See https://stackoverflow.com/a/32514167
        def wrapper():
            if request.path != "/upload":
                return
            if not "local_variables" in g:
                g.local_variables = {}
            if not "api_session_token" in request.headers\
                or not self.db.is_session_key_in_db(request.headers.get("api_session_token")):
                print("Generating new key")
                key = self.generate_session_key()
                g.local_variables["api_session_token"] = key
            else:
                g.local_variables["api_session_token"] = request.headers.get("api_session_token")
        return wrapper

    def generate_after_request_handler(self):
        def wrapper(response):
            if not hasattr(g, "local_variables") or "api_session_token" not in g.local_variables:
                return response
            key = g.local_variables.pop("api_session_token")
            response.headers["api_session_token"] = key
            return response
        return wrapper
