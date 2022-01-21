"""Module contains Resource to get the current kmeans centroids and change the amount of centroids"""
from flask import request
from flask_restful import Resource, abort

import api_package.db as db
import api_package.kmeans as kmeans


class ChangeNumberOfKMeansCentroids(Resource):
    """Resource returns the current kmeans centroids (GET) and change the amount of centroids (POST)"""
    
    def post(self):
        """HTTP POST request used to change the amount of cluster centers used in kmeans clustering

        Returns:
            Any: data for response
        """
        if not "nr_of_centroids" in request.json:
            abort(404, message="No nr_of_centroids in json body")
        nr_of_centroids = request.json["nr_of_centroids"]
        if nr_of_centroids is None:
            abort(404, message="No value for number of centroids given")
        try:
            nr_of_centroids = int(nr_of_centroids)
        except ValueError as e:
            abort(404, message=f"{e}\nError parsing nr_of_centroids {nr_of_centroids}")
        kmeans.get_instance().cluster(nr_of_centroids)
        db.get_instance().update_labels(kmeans.get_instance().labels)
        return f"k-means now uses {len(kmeans.get_instance().cluster_centers)} centroids"

    def get(self):
        """HTTP GET request used to get the amount and values of cluster centers

        Returns:
            Any: data for response
        """
        cluster_list = [ 
            { 
                "id": idx, 
                "cluster_center": item 
            } for idx, item in enumerate(kmeans.get_instance().cluster_centers.tolist()) 
        ]
        return {
            "nr_of_centroids": len(cluster_list),
            "cluster_centers": cluster_list
        }
