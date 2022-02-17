"""Main file to setup and start the backend server. Also initializes all needed modules."""
# For basic functionality we expanded and modified the example 
# from https://flask-restful.readthedocs.io/en/latest/quickstart.html#a-minimal-api
# to fit our needs
# IMPORTANT set up conda environment before use -> INSTALL.md
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
import gc
from math import floor
from os import environ

from api.helper import load_images, analyse_dataset
from flask_swagger_ui import get_swaggerui_blueprint

if __name__ == "__main__":
    exit("Start via run.py!")

# Set up Flask App using cors
app = Flask(__name__)
CORS(
    app, 
    resources={r"/*": {"origins": "*"}}, 
    expose_headers=["Api-Session-Token", "Content-Type", "Content-Length"],
)
api = Api(app)

# Needed for secure client sessions
secret_key = environ.get("FLASK_SECRET_KEY")
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

# Import database, automatic setup
import api.db as db

# import tsne, automatic setup
import api.tsne as tsne

# Load images from dataset
flat_images_filenames, flat_images, load_success = load_images(environ.get("DATA_PATH"))

if not load_success:
    exit("Loading images failed, images sizes incorrect")
if flat_images.shape[0] < 1:
    exit("Need to have data in data folder!")

# Calculate coordinates using tsne
coordinates = tsne.get_instance().initialize_coordinates(flat_images)

# Checks for amount of centroids
num_centroids = environ.get("NUM_CENTROIDS")
centroids_vaild = True
if num_centroids is None:
    print("Please update your .env file! Missing number of centroids, using default value")
    centroids_vaild = False
else:
    try:
        num_centroids = int(num_centroids)
        if num_centroids > flat_images.shape[0] or num_centroids < 0:
            print(f"Invalid value for number of centroids with {num_centroids}, using default value")
            centroids_vaild = False
    except ValueError as e:
        print(e, "\nError casting number of centroids for kmeans, using default value")
        centroids_vaild = False
if not num_centroids:
    num_centroids = int(max(floor(flat_images.shape[0] / 39), 1))
print(f"Using {num_centroids} as amount of cluster centers")

# Calculate clusters using kmeans
import api.kmeans as kmeans
kmeans.get_instance().initialize(coordinates)
kmeans.get_instance().cluster(int(num_centroids))

# Initialize database
db.get_instance().initialize(flat_images_filenames, coordinates, kmeans.get_instance().labels)

# Analyse dataset for possible later use
analyse_dataset(flat_images, coordinates)

del coordinates
gc.collect()

# Initialize faiss indices
# IndexFlatL2
import api.faiss as iss
flatL2_success = iss.get_instance().build_index(
    iss.get_instance().FlatL2, 
    flat_images_filenames, 
    flat_images,
    d=flat_images[0].shape[0]
    )
if not flatL2_success:
    exit("Failed building FlatL2 index")

# IndexIVFFlat
centroids = int(max(floor(flat_images.shape[0] / 39), 1))
probes_per_iteration = int(max(centroids / 10, 1))
ivfflat_success = iss.get_instance().build_index(
    iss.Faiss.IVFFlat, 
    flat_images_filenames, 
    flat_images,
    nlist=centroids, 
    nprobe=probes_per_iteration, 
    d=flat_images[0].shape[0]
    )
if not ivfflat_success:
    exit("Failed building IVFFlat index")

# Change current index to IndexFlatL2
assert iss.get_instance().change_index(iss.Faiss.FlatL2)

del flat_images
del flat_images_filenames
gc.collect()

# Initialize api session key generator
import api.authenticate as auth
app.before_request(auth.get_instance().generate_authenticator())
app.after_request(auth.get_instance().generate_after_request_handler())

# Paths
from api.resources import *

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
api.add_resource(GetSessionToken, "/authenticate")

def main(only_initialize: bool=False) -> None:
    """Used to start the backend server"""
    if only_initialize:
        print("Init done, returning")
        return
    print("Starting app")
    app.run(host=environ.get("BACKEND_HOST"), port=environ.get("BACKEND_PORT"), threaded=True)
