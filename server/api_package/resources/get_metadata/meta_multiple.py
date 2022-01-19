from flask_restful import Resource, abort
from flask import request
import api_package.db as db

class MetadataMultipleImages(Resource):
    """
    TODO docs
    """      
    def post(self):
        """
        TODO docs
        """
        picture_ids = request.json["picture_ids"]
        if picture_ids is None:
            abort(404, message="No picture ids present in json body")
        metadata = db.get_instance().get_multiple_metadata(picture_ids)
        if metadata is None:
            abort(404, message="An error occured while retrieving the metadata from the databse")
        return metadata