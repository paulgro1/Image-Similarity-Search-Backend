# For basic functionality we expanded and modified the example 
# from https://flask-restful.readthedocs.io/en/latest/quickstart.html#a-minimal-api
# to fit our needs
# IMPORTANT set up conda environment before use -> installation.txt
from flask import Flask, send_from_directory, url_for, send_file
from flask.globals import request
from flask_cors import CORS
from flask_restful import reqparse, abort, Resource, Api
from werkzeug.utils import secure_filename
import glob
import os

if __name__ == "__main__":
    exit("Start via run.py!")

# Allowed extensions for uploaded images
ALLOWED_EXTENSIONS = { "png", "jpg", "jpeg" }


# Set up Flask App using cors
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)

import api_package.db as db
database = db.Database()
database.initialize()

# TODO remove
upload_folder = os.environ.get("UPLOAD_FOLDER")
upload_folder_path = os.path.join(os.environ.get("SERVER_ROOT"), upload_folder)
if not os.path.isdir(upload_folder_path):
    os.mkdir(upload_folder_path)
app.config["UPLOAD_FOLDER"] = os.path.join(os.environ.get("SERVER_ROOT"), os.environ.get("UPLOAD_FOLDER"))


def abort_if_picture_doesnt_exist(picture_id):
    """
    Terminates request, if given picture_id does not correspond to a filename in FILENAMES
    
    Parameters
    ----------
    picture_id : int
        id of picture to be assessed
    """
    
    if not database.is_id_in_database(picture_id):
        abort(404, message=f"Picture {picture_id} not found")

def allowed_file(filename):
    """
    TODO docs
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class FullsizePicture(Resource):
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
        TODO return, docs
        """
        picture_id = int(picture_id)
        abort_if_picture_doesnt_exist(picture_id)
        print(f"Getting fullsize image { picture_id } ")
        image = database.get_one_fullsize_by_id(picture_id)
        if image == None:
            abort(404, message=f"Picture {picture_id} not found")
        return send_file(image["fullsize"])

class ThumbnailPicture(Resource):
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
        TODO return, docs
        """
        picture_id = int(picture_id)
        abort_if_picture_doesnt_exist(picture_id)
        print(f"Getting image thumbnail { picture_id } ")
        image = database.get_one_thumbnail_by_id(picture_id)
        if image == None:
            abort(404, message=f"Picture {picture_id} not found")
        return send_file(image["thumbnail"])

class AllPictureIDs(Resource):
    """
    TODO Docs
    """
    def get(self):
        """
        TODO docs
        """
        all_ids = database.get_all_ids()
        if all_ids == None:
            abort(404, message="No Pictures found")
        return all_ids

class AllPicturesThumbnail(Resource):
    """
    TODO Docs
    """
    def get(self):
        """
        HTTP GET method, returns all images from database
        TODO return docs
        """
        all_images = database.get_all_thumbnails()
        if all_images == None:
            abort(404, message="No Pictures found")
        return all_images

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
api.add_resource(AllPictureIDs, "/images/ids")
api.add_resource(AllPicturesThumbnail, "/images/thumbnails/all")
api.add_resource(ThumbnailPicture, "/images/thumbnails/<picture_id>")
api.add_resource(FullsizePicture, "/images/<picture_id>")
api.add_resource(Query, "/upload")

def main():
    app.run(host=os.environ.get("BACKEND_HOST"), port=os.environ.get("BACKEND_PORT"))


