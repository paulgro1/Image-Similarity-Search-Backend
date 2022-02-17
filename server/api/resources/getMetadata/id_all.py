"""Module contains Resource to get ids of all images in database"""
from flask_restful import Resource, abort

import api.db as db


class AllPictureIDs(Resource):
    """Resource returns ids of all images in database on get request"""

    def get(self):
        """HTTP GET request used to return the ids of all images in the database

        Returns:
            Any: data for response
        """
        all_ids = db.get_instance().get_all_ids()
        if all_ids is None:
            abort(404, message="No Pictures found")
        all_ids_list = [ x["id"] for x in all_ids ]
        return all_ids_list
