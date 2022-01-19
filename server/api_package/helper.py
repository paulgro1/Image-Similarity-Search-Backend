from PIL import Image
from os import path, environ
from glob import iglob
import numpy as np
from functools import wraps
from time import time
from flask_restful import abort

if __name__ == "__main__":
    exit("Start via run.py!")


# See https://stackoverflow.com/a/27737385
def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print(f"func:{f.__name__} args:[{args}, {kw}] took: {te-ts:2.4f} sec")
        return result
    return wrap

# Allowed extensions for uploaded images
ALLOWED_EXTENSIONS = { "png", "jpg", "jpeg" }

def allowed_file(filename):
    """
    TODO docs
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def abort_if_pictures_dont_exist(picture_ids, db):
    """
    Terminates request, if given picture_id(s) is/are not present within the database
    
    Parameters
    ----------
    picture_id : int
        id of picture to be assessed
    """
    success, possible_missing_ids = db.are_all_ids_in_database(picture_ids)
    if not success:
        print(f"Image(s) with id(s) {possible_missing_ids} is/are not in the database!")
        abort(404, message=f"Picture(s) {possible_missing_ids} not found")

def is_k_valid(k, db, id_from_database=False):
    if k is None:
        return False, "k is None", k
    if not type(k) is int:
        try:
            k = int(k)
        except ValueError as e:
            abort(500, message=e)
    if k < 1:
        return False, f"{k} < 1, value too small"
    nr_of_files_in_database = db.count_documents_in_collection()
    if id_from_database:
        nr_of_files_in_database -= 1 # excluding the file itself
    if k > nr_of_files_in_database:
        return False, f"k {k} is bigger than the (other) {nr_of_files_in_database} images in the index!", k
    return True, None, k

def process_image(image):
    with Image.open(image) as img:
        image_shape = (img.width, img.height)
        converted_image = img.convert("RGB")
    resized_image = np.array(converted_image, dtype="float32").ravel()
    return resized_image, image_shape

def _load_images(the_path):
    filename_list = []
    image_list = []
    correct_shape = None
    for image in iglob(path.join(the_path, "*")):
        filename = path.split(image)[-1]
        resized_image, image_shape = process_image(image)
        if correct_shape is None:
            correct_shape = image_shape
        elif correct_shape != image_shape:
            return None, None, False, None
        filename_list.append(filename)
        image_list.append(resized_image)
    names = np.array(filename_list)
    images = np.array(image_list, dtype="float32")
    return names, images, True, correct_shape

def load_images(the_path):
    names, images, success, correct_shape = _load_images(the_path)
    if success and correct_shape is not None:
        environ["FULLSIZE_WIDTH"] = str(correct_shape[0])
        environ["FULLSIZE_HEIGHT"] = str(correct_shape[1])
    return names, images, True

def load_images_by_id(ids, db) -> tuple((bool, np.ndarray, list, str)):
    images = db.get_multiple_by_id(ids, None)
    if images is None:
        return False, None, None, "Error retrieving images from database"
    p_images = []
    all_images = []
    for image in images:
        p_image, _ = process_image(image["path"])
        p_images.append(p_image)
        all_images.append({
            "id": image["id"],
            "filename": image["filename"],
            "position": {
                "x": image["x"],
                "y": image["y"]
            },
            "cluster_center": image["cluster_center"]
        })
    p_images = np.array(p_images, dtype="float32")
    return True, p_images, all_images, None

def load_and_process_one_from_dataset(the_path):
    full_path = path.join(environ.get("DATA_PATH"), the_path)
    resized_image, _ = process_image(full_path)
    return np.array(resized_image, dtype="float32")

analysed_dataset = None

def get_analysed_dataset():
    global analysed_dataset
    return analysed_dataset

def analyse_dataset(images, coordinates):
    coord_min = np.amin(coordinates, axis=0)
    x_min = coord_min[0]
    y_min = coord_min[1]
    coord_max = np.amax(coordinates, axis=0)
    x_max = coord_max[0]
    y_max = coord_max[1]
    coord_average = np.sum(coordinates, axis=0) / coordinates.shape[0]
    x_average = coord_average[0]
    y_average = coord_average[1]
    global analysed_dataset; analysed_dataset = {
        "coordinates": {
            "min_x": x_min,
            "max_x": x_max,
            "min_y": y_min,
            "max_y": y_max,
            "average_x": x_average,
            "average_y": y_average
        },
        "images": {
            "amount_of_images": images.shape[0],
            "image_size": {
                "width": environ.get("FULLSIZE_WIDTH"),
                "height": environ.get("FULLSIZE_HEIGHT")
            },
            "thumbnail_size": {
                "width": environ.get("ACTUAL_THUMBNAIL_WIDTH"),
                "height": environ.get("ACTUAL_THUMBNAIL_HEIGHT")
            },    
        }
    }
    