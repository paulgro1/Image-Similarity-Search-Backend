"""Module contains Resource to get one fullsize image"""
from flask import send_file
from flask_restful import Resource, abort
from typing import Any

import api.db as db
from api.helper import abort_if_pictures_dont_exist


class OneFullsize(Resource):
    """Resource returns one fullsize image on post request"""

    def get(self, picture_id: Any):
        """HTTP GET request used to return one fullsize image specified by picture_id in path

        Args:
            picture_id (Any): id of image to be returned

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
        print(f"Getting fullsize image { picture_id } ")
        image = db.get_instance().get_one_fullsize_by_id(picture_id)
        if image is None:
            abort(404, message=f"Picture {picture_id} not found")
        return send_file(image["path"])
