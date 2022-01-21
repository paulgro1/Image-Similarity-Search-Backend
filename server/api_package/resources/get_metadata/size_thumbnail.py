"""Module contains Resource to get the size of thumbnails within the dataset"""
from flask_restful import Resource
from os import environ

class ThumbnailSize(Resource):
    """Resource returns the size of thumbnails within the dataset on get request"""
    
    def get(self):
        """HTTP GET request used to return the size of thumbnails within the dataset

        Returns:
            Any: data for response
        """
        return {
            "width": environ.get("ACTUAL_THUMBNAIL_WIDTH"),
            "height": environ.get("ACTUAL_THUMBNAIL_HEIGHT")
        }   
