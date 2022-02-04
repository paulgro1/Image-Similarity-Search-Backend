"""Module contains Resource to get the metadata from one image in the database"""
from flask_restful import Resource, abort
from typing import Any

import api.db as db


class MetadataOneImage(Resource):
    """Resource returns the metadata from one image in the database on get request"""
    
    def get(self, picture_id: Any):
        """HTTP GET request used to return the metadata from one image in the database

        Args:
            picture_id (Any): id of image whose metadata shall be returned

        Returns:
            Any: data for response
        """
        if picture_id is None:
            abort(404, message="No picture_id present in path")
        try:
            picture_id = int(picture_id)
        except ValueError as e:
            abort(404, message=f"{e}\n Parsing picture_id {picture_id} failed")
        data = db.get_instance().get_metadata(picture_id)
        if data is None:
            abort(404, message="An error occured")
        return data
