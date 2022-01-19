from flask import send_file
from flask_restful import Resource, abort
from api_package.helper import abort_if_pictures_dont_exist
import api_package.db as db

class OneFullsize(Resource):
    """
    TODO Docs
    """
    def get(self, picture_id):
        """
        HTTP GET method, returns 1 image from database

        Parameters
        ----------
        picture_id : int
            id of picture to be returned
        TODO return, docs
        """
        picture_id = int(picture_id)
        abort_if_pictures_dont_exist(picture_id, db.get_instance())
        print(f"Getting fullsize image { picture_id } ")
        image = db.get_instance().get_one_fullsize_by_id(picture_id)
        if image is None:
            abort(404, message=f"Picture {picture_id} not found")
        return send_file(image["path"])