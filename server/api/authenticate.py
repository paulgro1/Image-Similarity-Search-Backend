"""Module containing logic used to create and update the api session token"""
import base64
from collections.abc import Callable
from flask import g, request
import M2Crypto
from typing import Any

import api.db as db

if __name__ == "__main__":
    exit("Start via run.py!")

# The instance of SessionKeyAuthenticator created on startup
_instance = None


class SessionKeyAuthenticator(object):
    """Class containing methods to implement the api session token"""

    def __init__(self) -> None:
        """Initialize blank object, set object as _instance of module"""
        super().__init__()

        # Singletonesque pattern
        global _instance
        if _instance is None:
            _instance = self

    def generate_session_key(self) -> bytes:
        """Generate a random api session token using M2Crypto

        Returns:
            bytes: the random api session token
        """
        key = base64.b64encode(M2Crypto.m2.rand_bytes(16))
        
        # Check if api session token is already in database, retry if already in database
        while db.get_instance().is_session_key_in_db(key):
            key = base64.b64encode(M2Crypto.m2.rand_bytes(16))
        
        # Store api session token in database
        db.get_instance().insert_session_key(key)
        return key

    def generate_authenticator(self) -> 'Callable[[None], None]':
        """Method used to generate wrapper to be called before requests in current context. 
        Checks for existing Api-Session-Token in request and stores an existing one in flask g.

        Returns:
            f: function checking the request
        """
        # See https://stackoverflow.com/a/32514167
        def wrapper() -> None:
            """Check global flask request for Api-Session-Token, if in request: store in flask g."""
            # local variables dict needs to exist, create if it doesn't
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
                # No valid api session token in header, ignore for this request
                return
            g.local_variables["Api-Session-Token"] = key
        return wrapper

    def generate_after_request_handler(self) -> 'Callable[[Any], Any]':
        """Method used to generate wrapper to be called after requests in current context. 
        Checks for possible Api-Session-Token in flask g and sets it as a response header if it exists.

        Returns:
            f: function for modifying the response
        """
        def wrapper(response: Any) -> Any:
            """Checks for Api-Session-Token in flask g, possibly sets it as a respone header.

            Args:
                response: flask response

            Returns:
                response: flask response
            """
            if not hasattr(g, "local_variables") or "Api-Session-Token" not in g.local_variables:
                return response
            key = g.local_variables.pop("Api-Session-Token")
            print("key out:", key)
            response.headers["Api-Session-Token"] = key
            return response
        return wrapper

def get_instance() -> SessionKeyAuthenticator:
    """Return the current and preferably only instance of SessionKeyAuthenticator. If possible use this function to access the class methods of this class.

    Returns:
        SessionKeyAuthenticator: current instance of SessionKeyAuthenticator
    """
    return _instance

# Create the current and preferably only instance of SessionKeyAuthenticator
_instance = SessionKeyAuthenticator()
