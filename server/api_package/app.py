# For basic functionality we expanded and modified the example 
# from https://flask-restful.readthedocs.io/en/latest/quickstart.html#a-minimal-api
# to fit our needs
# IMPORTANT set up conda environment before use -> installation.txt
from flask import Flask, send_from_directory, url_for, send_file
from flask.globals import request
from flask_cors import CORS
from flask_restful import reqparse, abort, Resource, Api
from pymongo import message
from werkzeug.utils import secure_filename
import glob
import os
import io
from PIL import Image
import zipfile

if __name__ == "__main__":
    exit("Start via run.py!")

# Allowed extensions for uploaded images
ALLOWED_EXTENSIONS = { "png", "jpg", "jpeg" }


# Set up Flask App using cors
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)

import api_package.process_images as pi
flat_images_filenames, flat_images = pi.load_images(os.environ.get("DATA_PATH"))

import api_package.tsne as tsne
coordinates = tsne.calculate_coordinates(flat_images, True) # TODO True -> False for real coordinates, is slower

import api_package.db as db
database = db.Database(flat_images_filenames, coordinates)
database.initialize()

from api_package.faiss import Faiss
iss = Faiss(flat_images_filenames, flat_images)
iss.index(Faiss.FlatL2, d=flat_images[0].shape[0])
assert iss.has_index
iss.initialize_index()

def abort_if_picture_doesnt_exist(picture_id):
    """
    Terminates request, if given picture_id is not present within the database
    
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


class OneFullsize(Resource):
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
        return send_file(image["path"])

class OneThumbnail(Resource):
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
        return send_file(image, mimetype=image.content_type, attachment_filename=image.filename)

class AllThumbnails(Resource):
    """
    TODO Docs
    TODO change response
    """
    def get(self):
        """
        HTTP GET method, returns all images from database
        TODO return docs
        """
        all_images = database.get_all_thumbnails()
        if all_images == None:
            abort(404, message="No Pictures found")
        # See https://stackoverflow.com/questions/2463770/python-in-memory-zip-library
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for item in all_images:
                zip_file.writestr(item.filename, item.read())
        buffer.seek(0)
        return send_file(buffer, attachment_filename="thumbnails.zip", as_attachment=True)

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
        all_ids_list = [ x["id"] for x in all_ids ]
        return all_ids_list


# Adaptation of https://stackoverflow.com/questions/28982974/flask-restful-upload-image/42286669#42286669
class UploadOne(Resource):
    """
    See https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/
    TODO Docs
    """

    def post(self):
        """
        HTTP POST method, upload image to api
        
        TODO return
        """
        if "img" not in request.files:
            abort(404, message="No image found")
        if "k" not in request.form:
            abort(404, message="No k found")
        file = request.files["img"]
        k = int(request.form["k"])
        if file.filename == "":
            return "error no file send"
        if file and allowed_file(file.filename):
            processed = pi.process_image(file)
            D, I = iss.search(processed, k)
            return { "distances": D.tolist(), "ids": I.tolist() }
        return "error file not allowed"

class MetadataOneImage(Resource):
    """
    TODO docs
    """      
    def get(self, picture_id):
        """
        TODO docs
        """
        picture_id = int(picture_id)
        data = database.get_metadata(picture_id)
        if data == None:
            abort(404, message="An error occured")
        return data

class MetadataAllImages(Resource):
    """
    TODO docs
    """
    def get(self):
        """
        TODO docs
        """
        data = database.get_all_metadata()
        if data == None:
            abort(404, message="An error occured")
        return data


class Debug(Resource):
    """
    Temporary class for debugging TODO remove
    """
    def get(self):
        return "Server is running"

# Paths
api.add_resource(Debug, "/")
api.add_resource(AllPictureIDs, "/images/ids")
api.add_resource(AllThumbnails, "/images/thumbnails/all")
api.add_resource(MetadataAllImages, "/images/all/metadata")
api.add_resource(OneThumbnail, "/images/thumbnails/<picture_id>")
api.add_resource(OneFullsize, "/images/<picture_id>")
api.add_resource(MetadataOneImage, "/images/<picture_id>/metadata")
api.add_resource(UploadOne, "/upload")
#api.add_resource(None, "/faiss/getNN/<picture_id>") TODO

def main():
    app.run(host=os.environ.get("BACKEND_HOST"), port=os.environ.get("BACKEND_PORT"))


