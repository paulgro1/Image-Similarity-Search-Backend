from flask_restful import Resource
from os import environ

class ImagesSize(Resource):
    """
    TODO docs
    """
    def get(self):
        return {
            "width": environ.get("FULLSIZE_WIDTH"),
            "height": environ.get("FULLSIZE_HEIGHT")
        }