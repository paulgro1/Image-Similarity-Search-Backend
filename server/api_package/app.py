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

flat_images_filenames, flat_images, load_success = load_images(environ.get("DATA_PATH"))
if not load_success:
    abort(404, message="Loading images failed, images sizes incorrect")

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

def abort_if_pictures_dont_exist(picture_ids):
    """
    Terminates request, if given picture_id(s) is/are not present within the database
    
    Parameters
    ----------
    picture_id : int
        id of picture to be assessed
    """
    success, possible_missing_ids = database.are_all_ids_in_database(picture_ids)
    if not success:
        print(f"Image(s) with id(s) {possible_missing_ids} is/are not in the database!")
        abort(404, message=f"Picture(s) {possible_missing_ids} not found")


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
        abort_if_pictures_dont_exist(picture_id)
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
        abort_if_pictures_dont_exist(picture_id)
        print(f"Getting image thumbnail { picture_id } ")
        image = database.get_one_thumbnail_by_id(picture_id)
        
        if image is None:
            abort(404, message=f"Picture {picture_id} not found")
        return send_file(image, mimetype=image.content_type, attachment_filename=image.filename)

class MultipleThumbnails(Resource):
    """
    TODO Docs
    """
    def post(self):
        """
        HTTP GET method, returns multiple thumbnails from database

        TODO return, docs
        """
        picture_ids = request.json["picture_ids"]
        abort_if_pictures_dont_exist(picture_ids)
        print(f"Getting thumbnails for ids { picture_ids } ")
        images = database.get_multiple_thumbnails_by_id(picture_ids)
        if images is None:
            abort(404, message=f"Picture(s) {picture_ids} not found")
        # See https://stackoverflow.com/questions/2463770/python-in-memory-zip-library
        buffer = BytesIO()
        with ZipFile(buffer, "a", ZIP_DEFLATED, False) as zip_file:
            for item in images:
                zip_file.writestr(item.filename, item.read())
        buffer.seek(0)
        return send_file(buffer, attachment_filename="thumbnails.zip", as_attachment=True)

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
class Upload(Resource):
    """
    See https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/
    TODO Docs
    """

    def post(self):
        """
        HTTP POST method, upload image to api
        
        TODO return
        """
        if "k" not in request.form:
            abort(404, message="No k found")
        k = int(request.form["k"])
        if k < 1:
            abort(404, message=f"Need to have k > 0; {k} is invalid")
        nr_of_files = len(request.files)
        print(f"Uploaded {nr_of_files} file(s)")
        if nr_of_files == 0:
            abort(404, message="No images send")
        images = []
        correct_image_shape = (int(environ.get("FULLSIZE_WIDTH")), int(environ.get("FULLSIZE_HEIGHT")))
        for item in request.files.items():
            the_file = item[1]
            if allowed_file(the_file.filename):
                new_image, new_image_shape = process_image(the_file)
                if new_image_shape != correct_image_shape:
                    print(f"Image has incorrect size with {new_image_shape}")
                    abort(404, description=f"Image {item[0]} has incorrect shape with {new_image_shape} != {correct_image_shape}")
                images.append(new_image)
        nr_of_allowed_files = len(images)
        print(f"Uploaded {nr_of_allowed_files} allowed files")
        if nr_of_allowed_files == 0:
            abort(404, message="No allowed files send")
        coordinates = tsne.calculate_coordinates(images)
        D, I = iss.search(images, k)
        sim_percentages = get_similarities(D)
        return { 
            "distances": D.tolist(), 
            "ids": I.tolist(), 
            "coordinates": coordinates.tolist(),
            "similarities": sim_percentages
            }

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
        if k is None or k < 1:
            abort(404, message=f"k is missing valid value in request body with value {k}")
        k += 1 # Image exists in database and is found in nearest neighbour search, need to find one more to delete the image itself from neighbours
        converted_image = load_and_process_one_from_dataset(the_path)
        D, I = iss.search(converted_image, k)
        sim_percentages = get_similarities(D)
        spot = np.argwhere(I == picture_id) # searching for index of requested center image
        if spot.shape[0] == 0: # no spot found, remove last element in result arrays
            spot = I.shape[1] - 1
        else: # remove element at spot
            spot = spot[0, 1]
        # Remove requested Picture
        D = np.delete(D, obj=spot, axis=1)
        I = np.delete(I, obj=spot, axis=1)
        sim_percentages[0].pop(spot)
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

class MetadataMultipleImages(Resource):
    """
    TODO docs
    """      
    def post(self):
        """
        TODO docs
        """
        picture_ids = request.json["picture_ids"]
        if picture_ids is None:
            abort(404, message="No picture ids present in json body")
        metadata = database.get_multiple_metadata(picture_ids)
        if metadata is None:
            abort(404, message="An error occured while retrieving the metadata from the databse")
        return metadata

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

class ImagesSize(Resource):
    """
    TODO docs
    """
    def get(self):
        return {
            "width": environ.get("FULLSIZE_WIDTH"),
            "height": environ.get("FULLSIZE_HEIGHT")
        }

class Debug(Resource):
    """
    Temporary class for debugging TODO remove
    """
    def get(self):
        return "Server is running"

# Paths
api.add_resource(Debug, "/")
api.add_resource(AllPictureIDs, "/images/ids")
api.add_resource(ImagesSize, "/images/size")
api.add_resource(AllThumbnails, "/images/thumbnails/all")
api.add_resource(MultipleThumbnails, "/images/thumbnails/multiple")
api.add_resource(OneThumbnail, "/images/thumbnails/<picture_id>")
api.add_resource(MetadataAllImages, "/images/all/metadata")
api.add_resource(MetadataMultipleImages, "/images/multiple/metadata")
api.add_resource(OneFullsize, "/images/<picture_id>")
api.add_resource(MetadataOneImage, "/images/<picture_id>/metadata")
api.add_resource(Upload, "/upload")
api.add_resource(NNOfExistingImage, "/faiss/getNN/<picture_id>")

def main():
    print("Starting app")
    app.run(host=environ.get("BACKEND_HOST"), port=environ.get("BACKEND_PORT"))


