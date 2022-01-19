from flask_restful import Resource, abort
from flask.globals import request, g
from os import environ
from api_package.helper import allowed_file, is_k_valid, process_image
import api_package.db as db
import api_package.tsne as tsne
import api_package.faiss as iss
import api_package.kmeans as kmeans
from api_package.similarities import get_similarities

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
        success, error, k = is_k_valid(k, db.get_instance())
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
        session_token = g.local_variables.get("Api-Session-Token")
        new_ids = db.get_instance().get_next_ids(session_token, nr_of_allowed_files)
        coordinates = tsne.get_instance().calculate_coordinates(images)
        labels = kmeans.get_instance().predict(coordinates)
        D, I = iss.get_instance().search(images, k)
        sim_percentages = get_similarities(D)
        res = db.get_instance().ids_to_various(I, filename=True, cluster_center=True)
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