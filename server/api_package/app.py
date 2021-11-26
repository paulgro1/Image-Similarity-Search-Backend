# For basic functionality we expanded and modified the example 
# from https://flask-restful.readthedocs.io/en/latest/quickstart.html#a-minimal-api
# to fit our needs
# IMPORTANT set up conda environment before use -> installation.txt
from flask import Flask, send_file
from flask.globals import request
from flask_cors import CORS
from flask_restful import abort, Resource, Api
from os import environ
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from api_package.similarities import get_similarities
from api_package.image_helper import process_image, load_images, load_and_process_one_from_dataset, allowed_file
import numpy as np

if __name__ == "__main__":
    exit("Start via run.py!")

# Set up Flask App using cors
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)

from api_package.db import Database
database = Database()
from api_package.tsne import TSNE
tsne = TSNE()

flat_images_filenames, flat_images = load_images(environ.get("DATA_PATH"))

if not database.is_initialized:
    coordinates = tsne.initialize_coordinates(flat_images)
    database.initialize(flat_images_filenames, coordinates)
    tsne.save_to_database(database)
else:
    tsne.load_from_database(database)

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
        if image is None:
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
        
        if image is None:
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
        if all_images is None:
            abort(404, message="No Pictures found")
        # See https://stackoverflow.com/questions/2463770/python-in-memory-zip-library
        buffer = BytesIO()
        with ZipFile(buffer, "a", ZIP_DEFLATED, False) as zip_file:
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
        if all_ids is None:
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
            processed = process_image(file)
            coordinates = tsne.calculate_coordinates(processed)
            D, I = iss.search(processed, k)
            sim_percentages = get_similarities(D)
            return { 
                "distances": D.tolist(), 
                "ids": I.tolist(), 
                "coordinates": coordinates.tolist(),
                "similarities": sim_percentages
                }
        return "error file not allowed"

class NNOfExistingImage(Resource):
    """
    TODO docs
    """      
    def post(self, picture_id):
        """
        TODO docs
        """
        picture_id = int(picture_id)
        image = database.get_one_fullsize_by_id(picture_id)
        if image is None:
            abort(404, message=f"Picture {picture_id} not found")
        the_path = image["path"]
        k = request.json["k"]
        if k is None or k < 0:
            abort(404, message=f"k is missing valid value in request body with value {k}")
        k += 1 # Image exists in database and is found in nearest neighbour search, need to find one more to delete the image itself from neighbours
        converted_image = load_and_process_one_from_dataset(the_path)
        D, I = iss.search(converted_image, k)
        sim_percentages = get_similarities(D)
        # Remove requested Picture
        assert I[0, 0] == picture_id
        D = np.delete(D, obj=0, axis=1)
        I = np.delete(I, obj=0, axis=1)
        sim_percentages[0].pop(0)
        return {
            "distances": D.tolist(),
            "ids": I.tolist(),
            "similarities": sim_percentages
        }

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
        if data is None:
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
        if data is None:
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
api.add_resource(NNOfExistingImage, "/faiss/getNN/<picture_id>")

def main():
    print("Starting app")
    app.run(host=environ.get("BACKEND_HOST"), port=environ.get("BACKEND_PORT"))


