# For basic functionality we expanded and modified the example 
# from https://flask-restful.readthedocs.io/en/latest/quickstart.html#a-minimal-api
# to fit our needs
# IMPORTANT set up conda environment before use -> installation.txt
from flask import Flask, send_from_directory, url_for
from flask.globals import request
from flask_cors import CORS
from flask_restful import reqparse, abort, Resource, Api
from werkzeug.utils import secure_filename
import glob
import os
from dotenv import load_dotenv

load_dotenv()

ALLOWED_EXTENSIONS = { "png", "jpg", "jpeg" }

# TODO remove hardcoded pictures, use database.
FILENAMES = { idx: url for idx, url in enumerate(glob.iglob(pathname="Faces Dataset/*")) }

# Set up Flask App using cors
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)

app.config["UPLOAD_FOLDER"] = os.environ.get("UPLOAD_FOLDER")


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

def allowed_file(filename):
    """
    TODO docs
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    See https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/
    TODO Docs
    """

    def post(self):
        """
        HTTP POST method, upload image to api
        
        TODO return
        """
        print(request.files)
        if "img" not in request.files:
            return "error no attached file found"
        file = request.files["img"]
        if file.filename == "":
            return "error no file send"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return "success"
        return "error file not allowed"

        
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
    app.run(host=os.environ.get("BACKEND_HOST"), port=os.environ.get("BACKEND_PORT"))
