"""Module contains Resource to get one thumbnail"""
from flask import send_file
from flask_restful import Resource, abort

import api_package.db as db
from api_package.helper import abort_if_pictures_dont_exist


class OneThumbnail(Resource):
    """Resource returns one thumbnail on get request"""

    def get(self, picture_id):
        """HTTP GET request used to return one thumbnail specified by picture_id in path

        Args:
            picture_id (Any): id of image whose thumbnail shall be returned

        Returns:
            Any: data for response
        """
        if picture_id is None:
            abort(404, message="No picture_id present in path")
        try:
            picture_id = int(picture_id)
        except ValueError as e:
            abort(404, message=f"{e}\n Parsing picture_id {picture_id} failed")
        abort_if_pictures_dont_exist(picture_id, db.get_instance())
        print(f"Getting image thumbnail { picture_id } ")
        image = db.get_instance().get_one_thumbnail_by_id(picture_id)
        
        if image is None:
            abort(404, message=f"Picture {picture_id} not found")
        return send_file(image, mimetype=image.content_type, attachment_filename=image.filename)
