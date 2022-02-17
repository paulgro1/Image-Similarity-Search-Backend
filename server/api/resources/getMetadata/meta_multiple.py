"""Module contains Resource to get the metadata of multiple images in the database"""
from flask import request
from flask_restful import Resource, abort

import api.db as db


class MetadataMultipleImages(Resource):
    """Resource returns the metadata of multiple images in the database on post request"""
    
    def post(self):
        """HTTP POST request used to return the metadata of multiple images in the database

        Returns:
            Any: data for response
        """
        if not "picture_ids" in request.json:
            abort(404, message="No picture ids present in json body")
        picture_ids = request.json["picture_ids"]
        metadata = db.get_instance().get_multiple_metadata(picture_ids)
        if metadata is None:
            abort(404, message="An error occured while retrieving the metadata from the databse")
        return metadata
