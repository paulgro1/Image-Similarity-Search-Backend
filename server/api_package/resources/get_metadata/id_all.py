from flask_restful import Resource, abort
import api_package.db as db


class AllPictureIDs(Resource):
    """
    TODO Docs
    """
    def get(self):
        """
        TODO docs
        """
        all_ids = db.get_instance().get_all_ids()
        if all_ids is None:
            abort(404, message="No Pictures found")
        all_ids_list = [ x["id"] for x in all_ids ]
        return all_ids_list
