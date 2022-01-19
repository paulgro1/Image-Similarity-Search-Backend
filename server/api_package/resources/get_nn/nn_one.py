from flask_restful import Resource, abort
from flask import request
import numpy as np
import api_package.db as db
import api_package.faiss as iss
from api_package.helper import load_and_process_one_from_dataset, is_k_valid
from api_package.similarities import get_similarities

class NNOfExistingImage(Resource):
    """
    TODO docs
    """      
    def post(self, picture_id):
        """
        TODO docs
        """
        picture_id = int(picture_id)
        image = db.get_instance().get_one_fullsize_by_id(picture_id)
        if image is None:
            abort(404, message=f"Picture {picture_id} not found")
        the_path = image["path"]
        if not "k" in request.json:
            abort(404, message="k is missing in request body")
        k = int(request.json["k"])
        success, error, k = is_k_valid(k, db.get_instance(), id_from_database=True)
        if not success:
            abort(404, message=error)
        k += 1  # Image exists in database and is found in nearest neighbour search, need to find one more to delete the image itself from neighbours
        converted_image = load_and_process_one_from_dataset(the_path)
        D, I = iss.get_instance().search(converted_image, k)
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
        res = db.get_instance().ids_to_various(I, filename=True, cluster_center=True)
        neighbour_filenames = res["filename"]
        neighbour_cluster_centers = res["cluster_center"]
        cluster_center = db.get_instance().get_one_label(picture_id)
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