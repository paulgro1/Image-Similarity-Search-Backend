import M2Crypto
import base64
from flask import g, request
import api_package.db as db
from collections.abc import Callable
from typing import Any

if __name__ == "__main__":
    exit("Start via run.py!")

_instance = None


class SessionKeyAuthenticator(object):

    def __init__(self) -> None:
        super().__init__()

        # Singletonesque pattern
        global _instance
        if _instance is None:
            _instance = self

    def generate_session_key(self) -> bytes:
        key = base64.b64encode(M2Crypto.m2.rand_bytes(16))
        while db.get_instance().is_session_key_in_db(key):
            key = base64.b64encode(M2Crypto.m2.rand_bytes(16))
        db.get_instance().insert_session_key(key)
        return key

    def generate_authenticator(self) -> Callable[[None], None]:
        # See https://stackoverflow.com/a/32514167
        def wrapper():
            if not "local_variables" in g:
                g.local_variables = {}
            key = None
            if "Api-Session-Token" in request.headers\
                and request.headers["Api-Session-Token"] != "undefined":
                key = request.headers["Api-Session-Token"].encode("utf-8")
                print("key in:", key)
                if not db.get_instance().is_session_key_in_db(key):
                    print("Generating new key")
                    key = self.generate_session_key() 
            else:
                return
            g.local_variables["Api-Session-Token"] = key
        return wrapper

    def generate_after_request_handler(self) -> Callable[[Any], Any]:
        def wrapper(response: Any):
            if not hasattr(g, "local_variables") or "Api-Session-Token" not in g.local_variables:
                return response
            key = g.local_variables.pop("Api-Session-Token")
            print("key out:", key)
            response.headers["Api-Session-Token"] = key
            return response
        return wrapper

def get_instance() -> SessionKeyAuthenticator:
    return _instance

_instance = SessionKeyAuthenticator()
