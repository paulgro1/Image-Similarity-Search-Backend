"""Module contains Resource to get multiple/all nearest neighbours of images within the database"""
from flask import request
from flask_restful import Resource, abort
import numpy as np
from typing import Any, Tuple, Literal, Union, NoReturn

import api.db as db
import api.faiss as iss
from api.helper import is_k_valid, load_images_by_id, abort_if_pictures_dont_exist
from api.similarities import get_similarities_as_array

def verify_k(k: Any) -> 'Union[Tuple[Literal[True], int, None], Tuple[Literal[False], None, str]]':
    """Function is used to check the validity of a given k, k being the amount of nearest neighbours to be calculated

    Args:
        k (Any): desired amount of nearest neighbours. Will be casted as an int

    Returns:
        bool: True if successful, False if an error occured
        int_or_None: int k if successful, None if an error occured
        None_or_str: None if successful, str containing error message if an error occured
    """
    success, error, k = is_k_valid(k, db.get_instance(), id_from_database=True)
    if not success:
        return False, None, error
    k += 1  # Image(s) exist(s) in database and is found in nearest neighbour search, need to find one more to delete the image itself from neighbours
    return True, k, None

class NNOfExistingImages(Resource):
    """Resource returns the neighbours of multiple (POST) or all (GET) images in the database"""

    def multiple(self, k: Any, ids: 'list[int]') -> 'Union[dict, NoReturn]':
        """Method used by both get and post, finding the nearest neighbours for all ids within "ids"

        Args:
            k (Any): amount of nearest neighbours
            ids (list (int)): list of ids from images, whose nearest neighbours shall be returned

        Returns:
            dict: dict containing the data concerning the nearest neighbour calculation
        """        
        k_success, k, error = verify_k(k)
        if not k_success:
            abort(404, message=error)
        load_success, images, description, error = load_images_by_id(ids, db.get_instance())
        if not load_success:
            abort(500, message=f"{error}\nAn error occured while loading the images")
        print(f"Searching with shape {images.shape}")
        D, I = iss.get_instance().search(images, k)
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
            
            res = db.get_instance().ids_to_various(nn, filename=True, cluster_center=True)
            desc["neighbour_filenames"] = res["filename"][0]
            desc["neighbour_cluster_centers"] = res["cluster_center"][0]
        return description

    def get(self, k):
        """
        Method used for returning the nearest neighbours of all images in database
        
        Args:
            k (Any): amount of nearest neighbours
        
        Returns:
            Any: data for response
        """
        if db.get_instance().is_db_empty():
            abort(404, message="No images in database")
        ids = [ item["id"] for item in db.get_instance().get_all_ids() ]
        return self.multiple(k, ids)

    def post(self, k):
        """
        Method used for returning the nearest neighbours of all images specified in body in picture_ids
        
        Args:
            k (Any): amount of nearest neighbours
        
        Returns:
            Any: data for response
        """
        if db.get_instance().is_db_empty():
            abort(404, message="No images in database")
        if not "picture_ids" in request.json:
            abort(404, message="No picture_ids present in json body!")
        ids = [ int(the_id) for the_id in request.json["picture_ids"] ]
        abort_if_pictures_dont_exist(ids, db.get_instance())
        return self.multiple(k, ids)
