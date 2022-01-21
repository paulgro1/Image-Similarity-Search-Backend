"""Module contains Resource to get all available faiss index keys"""
from flask_restful import Resource

import api_package.faiss as iss


class GetAllFaissIndices(Resource):
    """Resource returns all available faiss index keys on get request"""

    def get(self):
        """HTTP GET request used to return all available faiss index keys

        Returns:
            Any: data for response
        """
        return iss.get_instance().get_all_indices_keys()