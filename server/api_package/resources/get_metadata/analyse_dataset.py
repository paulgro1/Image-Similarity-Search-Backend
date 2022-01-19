from flask_restful import Resource
from api_package.helper import get_analysed_dataset

class AnalyseDataset(Resource):
    """
    TODO docs
    """
    def get(self):
        return get_analysed_dataset()