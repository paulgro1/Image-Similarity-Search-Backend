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

path = os.path.dirname(os.path.dirname(__file__))
data_folder = os.environ.get("DATA_FOLDER")

# Check if data folder is specified, creating one if specified and not yet a directory
if data_folder == None:
    print("You need to supply a directory name for the dataset in your .env file!")
    exit(0)
elif not os.path.isdir(os.path.join(path, data_folder)):
    os.mkdir(os.path.join(path, data_folder))
    print(f"Created empty directory { data_folder } for dataset. Please insert dataset.")

data_path = os.path.join(path, data_folder)
fullsize_path = os.path.join(data_path, os.environ.get("DATA_FULLSIZE_FOLDER"))
thumbnail_path = os.path.join(data_path, os.environ.get("DATA_THUMBNAILS_FOLDER"))



# Allowed extensions for uploaded images
ALLOWED_EXTENSIONS = { "png", "jpg", "jpeg" }

# TODO remove hardcoded pictures, use database.
FILENAMES = { idx: os.path.split(url)[-1] for idx, url in enumerate(glob.iglob(pathname=os.path.join(fullsize_path, "*"))) }

# Set up Flask App using cors
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)

# TODO remove
upload_folder = os.environ.get("UPLOAD_FOLDER")
upload_folder_path = os.path.join(path, upload_folder)
if not os.path.isdir(upload_folder_path):
    os.mkdir(upload_folder_path)
app.config["UPLOAD_FOLDER"] = os.path.join(path, os.environ.get("UPLOAD_FOLDER"))


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
        return send_from_directory(directory=fullsize_path, filename=filename)

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

def main():
    app.run(host=os.environ.get("BACKEND_HOST"), port=os.environ.get("BACKEND_PORT"))

if __name__ == "__main__":
    # TODO connect database and server -> correct download
    # TODO implement correct upload
    exit("Start via run.py!")
    main()
