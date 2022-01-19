from flask_restful import Resource
from flask import make_response
import api_package.authenticate as auth

class GetSessionToken(Resource):

    def get(self):
        resp = make_response("success")
        resp.headers["Api-Session-Token"] = auth.get_instance().generate_session_key()
        return resp