"""Module contais resource to change the current faiss index"""
from flask_restful import Resource, abort
from typing import Any

import api.faiss as iss


class ChangeActiveFaissIndex(Resource):
    """Resource changes the currently used faiss index on get request"""

    def get(self, index_key: Any):
        """HTTP GET request used to change the currently used faiss index

        Args:
            index_key (Any): key for faiss index

        Returns:
            Any: data for response
        """
        if index_key is None:
            abort(404, message="no index key send")
        try:
            index_key = str(index_key)
        except ValueError as e:
            abort(404, message=f"{e}\nError parsing index_key {index_key}")
        success = iss.get_instance().change_index(index_key)
        if success:
            return "success!"
        else:
            abort(404, message="index change failed")
