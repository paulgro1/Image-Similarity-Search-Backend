import M2Crypto
import base64
from flask import g, request

if __name__ == "__main__":
    exit("Start via run.py!")

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
            if request.path != "/upload":  # TODO remove
                print("not upload")
                return
            if not "local_variables" in g:
                g.local_variables = {}
            key = None
            if "Api-Session-Token" in request.headers\
                and request.headers["Api-Session-Token"] != "undefined":
                key = request.headers["Api-Session-Token"].encode("utf-8")
                print("key in:", key)
                if not self.db.is_session_key_in_db(key):
                    print("Generating new key")
                    key = self.generate_session_key() 
            else:
                return
            g.local_variables["Api-Session-Token"] = key
        return wrapper

    def generate_after_request_handler(self):
        def wrapper(response):
            if not hasattr(g, "local_variables") or "Api-Session-Token" not in g.local_variables:
                return response
            key = g.local_variables.pop("Api-Session-Token")
            print("key out:", key)
            response.headers["Api-Session-Token"] = key
            return response
        return wrapper
