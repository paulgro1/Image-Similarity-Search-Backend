from flask_restful import Resource, abort
from flask import request
import api_package.kmeans as kmeans
import api_package.db as db

class ChangeNumberOfKMeansCentroids(Resource):
    """
    TODO docs
    """
    def post(self):
        nr_of_centroids = request.json["nr_of_centroids"]
        if nr_of_centroids is None:
            abort(404, message="No value for number of centroids given")
        kmeans.get_instance().cluster(int(nr_of_centroids))
        db.get_instance().update_labels(kmeans.get_instance().labels)
        return f"k-means now uses {len(kmeans.get_instance().cluster_centers)} centroids"

    def get(self):
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