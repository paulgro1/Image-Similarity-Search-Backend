from flask_restful import Resource
import api_package.faiss as iss

class GetAllFaissIndices(Resource):
    """
    TODO docs
    """
    def get(self):
        return iss.get_instance().get_all_indices_keys()