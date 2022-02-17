"""Module contains Resource to get the metadata of all images within the database"""
from flask_restful import Resource, abort

import api.db as db


class MetadataAllImages(Resource):
    """Resource returns the metadata of all images within the database on get request"""

    def get(self):
        """HTTP GET request used to return the metadata of all images within the database

        Returns:
            Any: data for response
        """
        data = db.get_instance().get_all_metadata()
        if data is None:
            abort(404, message="An error occured")
        return data