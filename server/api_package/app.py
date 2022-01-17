# For basic functionality we expanded and modified the example 
# from https://flask-restful.readthedocs.io/en/latest/quickstart.html#a-minimal-api
# to fit our needs
# IMPORTANT set up conda environment before use -> installation.txt
from flask import Flask, send_file
from flask.globals import request, g
from flask_cors import CORS
from flask_restful import abort, Resource, Api
from os import environ, path, mkdir
from shutil import rmtree
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from api_package.similarities import get_similarities, get_similarities_as_array
from api_package.helper import process_image, load_images, load_and_process_one_from_dataset, allowed_file, analyse_dataset, load_images_by_id
import numpy as np
from math import floor
import gc
from PIL import Image
from flask_swagger_ui import get_swaggerui_blueprint

if __name__ == "__main__":
    exit("Start via run.py!")

# Set up Flask App using cors
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)

secret_key = environ["FLASK_SECRET_KEY"]
if not secret_key:
    exit("No secret key present!")
app.config["SECRET_KEY"] = secret_key

# https://sean-bradley.medium.com/add-swagger-ui-to-your-python-flask-api-683bfbb32b36
### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yml'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Image Similarity Search Backend"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###

from api_package.db import Database
database = Database()
from api_package.tsne import TSNE
tsne = TSNE()

flat_images_filenames, flat_images, load_success = load_images(environ.get("DATA_PATH"))

if not load_success:
    exit("Loading images failed, images sizes incorrect")
if flat_images.shape[0] < 1:
    exit("Need to have data in data folder!")

coordinates = tsne.initialize_coordinates(flat_images)
num_centroids = environ.get("NUM_CENTROIDS")
if num_centroids is None:
    exit("Please update your .env file! Missing number of centroids")
from api_package.kmeans import KMeansWrapper
kmeans = KMeansWrapper(coordinates)
kmeans.cluster(int(num_centroids))
database.initialize(flat_images_filenames, coordinates, kmeans.labels)

analysed_dataset = analyse_dataset(flat_images, coordinates)

del coordinates
gc.collect()

from api_package.faiss import Faiss
iss = Faiss()
flatL2_success = iss.build_index(
    Faiss.FlatL2, 
    flat_images_filenames, 
    flat_images,
    d=flat_images[0].shape[0]
    )
if not flatL2_success:
    exit("Failed building FlatL2 index")

centroids = int(max(floor(flat_images.shape[0] / 39), 1))
probes_per_iteration = int(max(centroids / 10, 1))
ivfflat_success = iss.build_index(
    Faiss.IVFFlat, 
    flat_images_filenames, 
    flat_images,
    nlist=centroids, 
    nprobe=probes_per_iteration, 
    d=flat_images[0].shape[0]
    )
if not ivfflat_success:
    exit("Failed building IVFFlat index")

assert iss.change_index(Faiss.FlatL2)

del flat_images
del flat_images_filenames
gc.collect()

from api_package.authenticate import SessionKeyAuthenticator
auth = SessionKeyAuthenticator(database)
app.before_request(auth.generate_authenticator())
app.after_request(auth.generate_after_request_handler())

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

class MultipleFullsize(Resource):
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
        print(f"Getting fullsize for ids { picture_ids } ")
        images = database.get_multiple_fullsize_by_id(picture_ids)
        if images is None:
            abort(404, message=f"Picture(s) {picture_ids} not found")
        # See https://stackoverflow.com/questions/2463770/python-in-memory-zip-library
        buffer = BytesIO()
        with ZipFile(buffer, "a", ZIP_DEFLATED, False) as zip_file:
            for item in images:
                with Image.open(item["path"]) as img:
                    filename = path.split(item["path"])[-1]
                    with BytesIO() as output:
                        img.save(output, format=img.format)
                        the_id = item["id"]
                        zip_file.writestr(f"{the_id}_{filename}", output.getvalue())
        buffer.seek(0)
        return send_file(buffer, attachment_filename="fullsize.zip", as_attachment=True)

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
                the_id = item.id
                zip_file.writestr(f"{the_id}_{item.filename}", item.read())
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
                the_id = item.id
                zip_file.writestr(f"{the_id}_{item.filename}", item.read())
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

def is_k_valid(k, id_from_database=False):
    if k is None:
        return False, "k is None", k
    if not type(k) is int:
        try:
            k = int(k)
        except ValueError as e:
            abort(500, message=e)
    if k < 1:
        return False, f"{k} < 1, value too small"
    nr_of_files_in_database = database.count_documents_in_collection()
    if id_from_database:
        nr_of_files_in_database -= 1 # excluding the file itself
    if k > nr_of_files_in_database:
        return False, f"k {k} is bigger than the (other) {nr_of_files_in_database} images in the index!", k
    return True, None, k

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
        if not "k" in request.form:
            abort(404, message="No k found")
        k = request.form["k"]
        success, error, k = is_k_valid(k)
        if not success:
            abort(404, message=error)
        print("k is", k)
        nr_of_files = len(request.files)
        print(f"Uploaded {nr_of_files} file(s)")
        if nr_of_files == 0:
            abort(404, message="No images send")
        images = []
        filenames = []
        correct_image_shape = (int(environ.get("FULLSIZE_WIDTH")), int(environ.get("FULLSIZE_HEIGHT")))
        for item in request.files.items():
            the_file = item[1]
            if allowed_file(the_file.filename):
                filenames.append(the_file.filename)
                new_image, new_image_shape = process_image(the_file)
                if new_image_shape != correct_image_shape:
                    print(f"Image has incorrect size with {new_image_shape}")
                    abort(404, description=f"Image {item[0]} has incorrect shape with {new_image_shape} != {correct_image_shape}")
                images.append(new_image)
        nr_of_allowed_files = len(images)
        print(f"Uploaded {nr_of_allowed_files} allowed files")
        if nr_of_allowed_files == 0:
            abort(404, message="No allowed files send")
        new_ids = database.get_next_ids(g.local_variables.get("api_session_token"), nr_of_allowed_files)
        coordinates = tsne.calculate_coordinates(images)
        labels = kmeans.predict(coordinates)
        D, I = iss.search(images, k)
        sim_percentages = get_similarities(D)
        res = database.ids_to_various(I, filename=True, cluster_center=True)
        neighbour_filenames = res["filename"]
        neighbour_cluster_centers = res["cluster_center"]
        return { 
            "uploaded_filenames": filenames,
            "new_ids": new_ids,
            "distances": D.tolist(), 
            "ids": I.tolist(), 
            "neighbour_filenames": neighbour_filenames,
            "neighbour_cluster_centers": neighbour_cluster_centers,
            "coordinates": coordinates.tolist(),
            "similarities": sim_percentages,
            "cluster_centers": labels.tolist()
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
        if not "k" in request.json:
            abort(404, message="k is missing in request body")
        k = int(request.json["k"])
        success, error, k = is_k_valid(k, id_from_database=True)
        if not success:
            abort(404, message=error)
        k += 1  # Image exists in database and is found in nearest neighbour search, need to find one more to delete the image itself from neighbours
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
        res = database.ids_to_various(I, filename=True, cluster_center=True)
        neighbour_filenames = res["filename"]
        neighbour_cluster_centers = res["cluster_center"]
        cluster_center = database.get_one_label(picture_id)
        return {
            "requested_id": picture_id,
            "requested_filename": image["filename"],
            "distances": D.tolist(),
            "ids": I.tolist(),
            "neighbour_filenames": neighbour_filenames,
            "neighbour_cluster_centers": neighbour_cluster_centers,
            "similarities": sim_percentages,
            "cluster_center": int(cluster_center)
        }

class NNOfExistingImages(Resource):
    """
    TODO docs
    """ 

    def verify_k(self, k):
        success, error, k = is_k_valid(k, id_from_database=True)
        if not success:
            return False, None, error
        k += 1  # Image(s) exist(s) in database and is found in nearest neighbour search, need to find one more to delete the image itself from neighbours
        return True, k, None

    def multiple(self, k, ids):
        """
        TODO docs
        """
        k_success, k, error = self.verify_k(k)
        if not k_success:
            abort(404, message=error)
        load_success, images, description, error = load_images_by_id(ids, database)
        if not load_success:
            abort(500, message="An error occured while loading the images")
        print(f"Searching with shape {images.shape}")
        D, I = iss.search(images, k)
        sim_percentages = get_similarities_as_array(D)
        for idx, id in enumerate(ids):
            desc = description[idx]
            assert desc["id"] == id
            nn = np.array(I[idx,:])
            dist = np.array(D[idx,:])
            sims = np.array(sim_percentages[idx,:])
            spot = np.argwhere(nn == id)
            if spot.shape[0] == 0:
                spot = nn.shape[1] - 1
            else:
                spot = spot[0]
            nn = np.delete(nn, obj=spot)
            dist = np.delete(dist, obj=spot)
            sims = np.delete(sims, obj=spot)
            desc["neighbour_ids"] = nn.tolist()
            desc["distances"] = dist.tolist()
            desc["similarities"]  = sims.tolist()
            res = database.ids_to_various(nn, filename=True, cluster_center=True)
            desc["neighbour_filenames"] = res["filename"][0]
            desc["neighbour_cluster_centers"] = res["cluster_center"][0]

        return description

    def get(self, k):
        """
        For all images in database
        TODO docs
        """
        if database.is_db_empty():
            abort(404, message="No images in database")
        ids = [ item["id"] for item in database.get_all_ids() ]
        return self.multiple(k, ids)


    def post(self, k):
        """
        For images specified in body in picture_ids
        TODO docs
        """
        if database.is_db_empty():
            abort(404, message="No images in database")
        if not "picture_ids" in request.json:
            abort(404, message="No picture_ids present in json body!")
        ids = [ int(the_id) for the_id in request.json["picture_ids"] ]
        abort_if_pictures_dont_exist(ids)
        return self.multiple(k, ids)
        
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

class ThumbnailSize(Resource):
    """
    TODO docs
    """
    def get(self):
        return {
            "width": environ.get("ACTUAL_THUMBNAIL_WIDTH"),
            "height": environ.get("ACTUAL_THUMBNAIL_HEIGHT")
        }    

class GetAllFaissIndices(Resource):
    """
    TODO docs
    """
    def get(self):
        return iss.get_all_indices_keys()


class ChangeActiveFaissIndex(Resource):
    """
    TODO docs
    """
    def post(self, index_key):
        if index_key is None:
            abort(404, message="no index key send")
        success = iss.change_index(index_key)
        if success:
            return "success!"
        else:
            abort(404, message="index change failed")

class AnalyseDataset(Resource):
    """
    TODO docs
    """
    def get(self):
        return analysed_dataset

class ChangeNumberOfKMeansCentroids(Resource):
    """
    TODO docs
    """
    def post(self):
        nr_of_centroids = request.json["nr_of_centroids"]
        if nr_of_centroids is None:
            abort(404, message="No value for number of centroids given")
        kmeans.cluster(int(nr_of_centroids))
        database.update_labels(kmeans.labels)
        return f"k-means now uses {len(kmeans.cluster_centers)} centroids"

    def get(self):
        cluster_list = [ 
            { 
                "id": idx, 
                "cluster_center": item 
            } for idx, item in enumerate(kmeans.cluster_centers.tolist()) 
        ]
        return {
            "nr_of_centroids": len(cluster_list),
            "cluster_centers": cluster_list
        }


# Paths
api.add_resource(AllPictureIDs, "/images/ids")
api.add_resource(ImagesSize, "/images/size")
api.add_resource(AnalyseDataset, "/images/analyseDataset")
api.add_resource(AllThumbnails, "/images/thumbnails/all")
api.add_resource(ThumbnailSize, "/images/thumbnails/size")
api.add_resource(MultipleThumbnails, "/images/thumbnails/multiple")
api.add_resource(OneThumbnail, "/images/thumbnails/<picture_id>")
api.add_resource(MetadataAllImages, "/images/all/metadata")
api.add_resource(MultipleFullsize, "/images/multiple")
api.add_resource(MetadataMultipleImages, "/images/multiple/metadata")
api.add_resource(OneFullsize, "/images/<picture_id>")
api.add_resource(MetadataOneImage, "/images/<picture_id>/metadata")
api.add_resource(Upload, "/upload")
api.add_resource(NNOfExistingImage, "/faiss/getNN/<picture_id>")
api.add_resource(NNOfExistingImages, "/faiss/getNN/multiple/<k>")
api.add_resource(GetAllFaissIndices, "/faiss/index/all")
api.add_resource(ChangeActiveFaissIndex, "/faiss/index/<index_key>")
api.add_resource(ChangeNumberOfKMeansCentroids, "/kmeans/centroids")

def main():
    print("Starting app")
    app.run(host=environ.get("BACKEND_HOST"), port=environ.get("BACKEND_PORT"), threaded=True)
