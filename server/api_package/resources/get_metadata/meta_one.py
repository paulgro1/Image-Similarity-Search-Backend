from flask_restful import Resource, abort
import api_package.db as db

class MetadataOneImage(Resource):
    """
    TODO docs
    """      
    def get(self, picture_id):
        """
        TODO docs
        """
        picture_id = int(picture_id)
        data = db.get_instance().get_metadata(picture_id)
        if data is None:
            abort(404, message="An error occured")
        return data