from flask_restful import Resource, abort
import api_package.faiss as iss

class ChangeActiveFaissIndex(Resource):
    """
    TODO docs
    """
    def post(self, index_key):
        if index_key is None:
            abort(404, message="no index key send")
        success = iss.get_instance().change_index(index_key)
        if success:
            return "success!"
        else:
            abort(404, message="index change failed")