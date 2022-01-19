from flask_restful import Resource, abort
import api_package.db as db

class MetadataAllImages(Resource):
    """
    TODO docs
    """
    def get(self):
        """
        TODO docs
        """
        data = db.get_instance().get_all_metadata()
        if data is None:
            abort(404, message="An error occured")
        return data