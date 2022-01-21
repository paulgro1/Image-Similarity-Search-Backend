"""Helper module containing functions used by different modules"""
from collections.abc import Callable
from flask_restful import abort
from functools import wraps
from glob import iglob
import numpy as np
from os import path, environ
from PIL import Image
from time import time
from typing import Any, Union, NoReturn, Literal, Tuple

if __name__ == "__main__":
    exit("Start via run.py!")


# See https://stackoverflow.com/a/27737385
def timing(f: 'Callable[[Any], Any]') -> 'Callable[[Any, Any], Any]':
    """Method times the execution of a function, shall be used as a decorator

    Returns:
        f: wrapper function
    """
    @wraps(f)
    def wrap(*args, **kw) -> Any:
        ts = time()
        result = f(*args, **kw)
        te = time()
        print(f"func:{f.__name__} args:[{args}, {kw}] took: {te-ts:2.4f} sec")
        return result
    return wrap

# Allowed extensions for uploaded images
ALLOWED_EXTENSIONS = { "png", "jpg", "jpeg" }

def allowed_file(filename: str) -> bool:
    """Checks if the file is valid. A dot (.) needs to be in the filename and the extension needs to be present in ALLOWED_EXTENSIONS

    Args:
        filename (str): [description]

    Returns:
        bool: [description]
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def abort_if_pictures_dont_exist(picture_ids: 'list[int]', db: Any) -> 'Union[None, NoReturn]':
    """Terminates request, if given picture_id(s) is/are not present within the database
    
    Args:
        picture_id (list (int)): ids of picture to be assessed
        db (api_package.db.Database): instance of the database
    """
    success, possible_missing_ids = db.are_all_ids_in_database(picture_ids)
    if not success:
        print(f"Image(s) with id(s) {possible_missing_ids} is/are not in the database!")
        abort(404, message=f"Picture(s) {possible_missing_ids} not found")

def is_k_valid(k: Any, db: Any, id_from_database: bool=False) -> 'Union[Tuple[Literal[True], None, int], Tuple[Literal[False], str, Union[int, None]]]':
    """Checks if a given value for k, k being amount of nearest neighbours to search in a faiss index, is valid.

    Args:
        k (Any): amount of desired nearest neighbours. Will be casted as an int, fails if an error occures
        db (api_package.db.Database): instance of the database
        id_from_database (bool): if True, the image to be searched for is already in the database, need to have 0 < k < db.count_documents_in_collection() - 1, 
        False if different image, need to have 0 < k < db.count_documents_in_collection()

    Returns:
        bool: True if successful, False if an error occured
        None_or_str: None if successful, str containing the error message if an error occured
        int: the (possibly casted) int value for k
    """
    if k is None:
        return False, "k is None", k
    if not type(k) is int:
        try:
            k = int(k)
        except ValueError as e:
            abort(500, message=e)
    if k < 1:
        return False, f"{k} < 1, value too small", k
    nr_of_files_in_database = db.count_documents_in_collection()
    if id_from_database:
        nr_of_files_in_database -= 1 # excluding the file itself
    if k > nr_of_files_in_database:
        return False, f"k {k} is bigger than the (other) {nr_of_files_in_database} images in the index!", k
    return True, None, k

def process_image(file_path: str) -> 'Tuple[np.ndarray, Tuple[int, int]]':
    """Convert an image indicated by its file_path to a flat np.ndarray

    Args:
        file_path (str): the path of the image

    Returns:
        np.ndarray: the flat image
        tuple (int, int): width, height of the original image
    """
    with Image.open(file_path) as img:
        image_shape = (img.width, img.height)
        converted_image = img.convert("RGB")
    resized_image = np.array(converted_image, dtype="float32").ravel()
    return resized_image, image_shape

def _load_images(the_path: str) -> 'Union[Tuple[np.ndarray, np.ndarray, Literal[True], Tuple[int, int]], Tuple[None, None, Literal[False], None]]':
    """Functions loads all images within the_path directory

    Args:
        the_path (str): path to the directory containing the images

    Returns:
        np.ndarray: array of the filenames or None if an error occured
        np.ndarray: array containing the flat images or None if an error occured
        bool: True if successful, False if an error occured
        tuple (int, int): width, height of all images or None if an error occured
    """
    if not path.isdir(the_path):
        return None, None, False, None
    filename_list = []
    image_list = []
    correct_shape = None
    for image in iglob(path.join(the_path, "*")):
        filename = path.split(image)[-1]
        resized_image, image_shape = process_image(image)
        # Check if image shape is correct
        if correct_shape is None:
            correct_shape = image_shape
        elif correct_shape != image_shape:
            return None, None, False, None
        filename_list.append(filename)
        image_list.append(resized_image)
    names = np.array(filename_list)
    images = np.array(image_list, dtype="float32")
    return names, images, True, correct_shape

def load_images(the_path: str) -> 'Tuple[Union[np.ndarray, None], Union[np.ndarray, None], Literal[True]]':
    """Call this function with a the_path to a directory containing images

    Args:
        the_path (str): path to the directory containing the images

    Returns:
        np.ndarray: array of the filenames or None if an error occured
        np.ndarray: array containing the flat images or None if an error occured
        bool: True if successful, False if an error occured
    """
    names, images, success, correct_shape = _load_images(the_path)
    if success and correct_shape is not None:
        environ["FULLSIZE_WIDTH"] = str(correct_shape[0])
        environ["FULLSIZE_HEIGHT"] = str(correct_shape[1])
        return names, images, True
    else:
        return None, None, False

def load_images_by_id(ids: 'list[int]', db: Any) -> 'Union[Tuple[Literal[True], np.ndarray, list[dict], None], Tuple[Literal[False], None, None, str]]':
    """Reload all images indicated by ids by getting the path from db

    Args:
        ids (list (int)): list containing the ids of the images within the database, prechecked
        db (api_package.db.Database): instance of the database

    Returns:
        bool: True if successful, False if an error occured
        np.ndarray: flat images or None if an error occured
        list (dict): list containing the metadata of the loaded images
        None_or_str: None if successful, str containing the error message if an error occured
    """
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

def load_and_process_one_from_dataset(the_path: str) -> np.ndarray:
    """Loads the image indicated by the_path and converts it to a flat array

    Args:
        the_path (str): path to the image

    Returns:
        np.ndarray: the flat image as an array
    """
    full_path = path.join(environ.get("DATA_PATH"), the_path)
    resized_image, _ = process_image(full_path)
    return np.array(resized_image, dtype="float32")

analysed_dataset = None

def get_analysed_dataset() -> 'Union[dict, None]':
    """Return the values calulated for the dataset

    Returns:
        dict_or_None: dict containing the values, if anaylse_dataset has been called, None otherwise
    """
    global analysed_dataset
    return analysed_dataset

def analyse_dataset(images: np.ndarray, coordinates: np.ndarray) -> dict:
    """Calculate the min, max and average coordinates. Return them and the amount of images and the width, height of thumbnails and fullsize images

    Args:
        images (np.ndarray): array containing all flat images
        coordinates (np.ndarray): array containing all coordinates calculated for images

    Returns:
        dict: contains the min, max and average coordinates, amount of images and width, height of images
    """
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
    