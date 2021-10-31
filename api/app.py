# For basic functionality we expanded and modified the example 
# from https://flask-restful.readthedocs.io/en/latest/quickstart.html#a-minimal-api
# to fit our needs
# IMPORTANT set up conda environment before use -> installation.txt
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_restful import reqparse, abort, Resource, Api
import werkzeug
import glob
import os

# TODO remove hardcoded pictures, use database.
FILENAMES = { idx: url for idx, url in enumerate(glob.iglob(pathname="Faces Dataset/*")) }

# Set up Flask App using cors
app = Flask(__name__)
CORS(app)
api = Api(app)


def abort_if_picture_doesnt_exist(picture_id):
    """
    Terminates request, if given picture_id does not correspond to a filename in FILENAMES
    
    Parameters
    ----------
    picture_id : int
        id of picture to be assessed
    """
    if picture_id not in FILENAMES:
        abort(404, message=f"Picture {picture_id} not found")

# Set up argument parser TODO arguments
parser = reqparse.RequestParser()
parser.add_argument("picture_id")
parser.add_argument("file", type=werkzeug.datastructures.FileStorage, location="files")


class Picture(Resource):
    """
    TODO Docs
    """
    def get(self, picture_id):
        """
        HTTP GET method, returns 1 image from database

        Parameters
        ----------
        picture_id : int
            id of picture to be returned
        TODO return
        """
        picture_id = int(picture_id)
        abort_if_picture_doesnt_exist(picture_id)
        filename = os.path.split(FILENAMES[picture_id])[1]
        print(f"Getting image { picture_id } -> { filename }")
        # TODO output correct?
        return send_from_directory(directory="../Faces Dataset", filename=filename)

class All_Pictures(Resource):
    """
    TODO Docs
    """
    def get(self):
        """
        HTTP GET method, returns all images from database
        TODO return
        """
        if len(FILENAMES) != 0:
            return FILENAMES
        else:
            abort(404, message="No Pictures found")

# Adaptation of https://stackoverflow.com/questions/28982974/flask-restful-upload-image/42286669#42286669
class Query(Resource):
    """
    TODO Docs
    """
    def options(self):
        """
        HTTP OPTIONS method
        TODO return, use
        """
        # TODO unwrap form
        print(parser.parse_args())
    
    def post(self):
        """
        HTTP POST method, upload image to api
        TODO return
        """
        # TODO unwrap form
        args = parser.parse_args()
        print(args)
        img = args["data"]
        print(img)

class Debug(Resource):
    """
    Temporary class for debugging TODO remove
    """
    def get(self):
        return "Server is running"

# Paths
api.add_resource(Debug, "/")
api.add_resource(Picture, "/images/<picture_id>")
api.add_resource(All_Pictures, "/images/all")
api.add_resource(Query, "/upload")

if __name__ == "__main__":
    # TODO refactor in .env
    app.run(host="0.0.0.0", port=8080)
