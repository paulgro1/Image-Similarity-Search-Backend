"""Module contains Resource to return the size of images within the dataset"""
from flask_restful import Resource
from os import environ


class ImagesSize(Resource):
    """Resource returns the size of images within the dataset"""

    def get(self):
        """HTTP GET request used to return the size of images within the dataset

        Returns:
            Any: data for response
        """
        return {
            "width": environ.get("FULLSIZE_WIDTH"),
            "height": environ.get("FULLSIZE_HEIGHT")
        }
