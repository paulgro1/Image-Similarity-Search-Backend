from flask_restful import Resource
from os import environ

class ThumbnailSize(Resource):
    """
    TODO docs
    """
    def get(self):
        return {
            "width": environ.get("ACTUAL_THUMBNAIL_WIDTH"),
            "height": environ.get("ACTUAL_THUMBNAIL_HEIGHT")
        }   