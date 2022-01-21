"""Module contains Resource to get a session token"""
from flask import make_response
from flask_restful import Resource

import api_package.authenticate as auth


class GetSessionToken(Resource):
    """Resource returns a new Api-Session-Token in its response header after a get request"""
    
    def get(self):
        """HTTP GET request returning a new Api-Session-Token in its response header

        Returns:
            Any: data for response
        """
        resp = make_response("success")
        resp.headers["Api-Session-Token"] = auth.get_instance().generate_session_key()
        return resp
