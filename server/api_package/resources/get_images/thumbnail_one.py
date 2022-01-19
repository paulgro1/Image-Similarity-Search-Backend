from flask_restful import Resource, abort
import api_package.db as db
from api_package.helper import abort_if_pictures_dont_exist
from flask import send_file


class OneThumbnail(Resource):
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
        print(f"Getting image thumbnail { picture_id } ")
        image = db.get_instance().get_one_thumbnail_by_id(picture_id)
        
        if image is None:
            abort(404, message=f"Picture {picture_id} not found")
        return send_file(image, mimetype=image.content_type, attachment_filename=image.filename)