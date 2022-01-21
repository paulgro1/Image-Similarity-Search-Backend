"""Module contains Resource to return data concerning coordinates and images in the dataset"""
from flask_restful import Resource

from api_package.helper import get_analysed_dataset


class AnalyseDataset(Resource):
    """Resource returns data concerning coordinates and images in the dataset"""

    def get(self):
        """HTTP GET request used to return data concerning coordinates and images in the dataset

        Returns:
            Any: data for response
        """
        return get_analysed_dataset()
