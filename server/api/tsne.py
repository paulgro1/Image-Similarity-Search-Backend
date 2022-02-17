"""Module uses t-SNE dimension reduction to convert multidimensional vectors into 2D points"""
import numpy as np
from openTSNE import TSNE as openTSNE
from os import environ
from sklearn.decomposition._pca import PCA
from typing import NoReturn, Union

if __name__ == "__main__":
    exit("Start via run.py!")

# The instance of TSNE created on startup
_instance = None

class TSNE(object):
    """Class that wraps the TSNE implemetation from openTSNE"""

    def __init__(self) -> None:
        """Initialize blank object, set object as _instance of module"""
        super().__init__()

        global _instance
        if _instance is None:
            _instance = self

    def initialize_coordinates(self, images: np.ndarray) -> 'Union[np.ndarray, NoReturn]':
        """Method used to calcutate the coordinates using PCA to reduce the dimensions to value specified in 
        environment variable REDUCE_IMAGES_TO_DIMS

        Args:
            images (np.ndarray): array of flat images

        Returns:
            np.ndarray: corresponding coordinates
        """
        print("Initializing Coordinates")
        np_images = np.array(images, dtype="float32")
        if np_images.ndim == 1:
            np_images = np_images.reshape(1, -1)
        nr_of_samples = np_images.shape[0]
        dims = environ.get("REDUCE_IMAGE_TO_DIMS")
        try:
            dims = int(dims)
        except ValueError as e:
            exit(e, f"\nParsing REDUCE_IMAGES_TO_DIMS failed with value {dims}")
        print(f"Reducing dimensions to {dims}")
        if dims > nr_of_samples:
            exit(f"Number of samples ({nr_of_samples}) needs to be greater or equal to the desired dimensions ({dims}) for PCA!")
        elif dims < 1:
            exit(f"REDUCE_IMAGE_TO_DIMS ({dims}) needs to be greater than 0!")
        self.pca = PCA(
            n_components=dims,
            random_state=123
            )
        reduced_images = self.pca.fit_transform(np_images)
        # https://www.reneshbedre.com/blog/tsne.html
        learningrate = max(nr_of_samples / 12, 200)
        perplexity = min(max(5, nr_of_samples / 10), 100)
        tsne = openTSNE(
            initialization="pca", 
            perplexity=perplexity, 
            metric="euclidean", 
            n_jobs=-1, 
            verbose=True, 
            neighbors="exact", 
            learning_rate=learningrate,
            random_state=123
            )
        images_embedded = tsne.fit(reduced_images)
        self.coordinates = images_embedded
        print("Coordinates initialized")
        return images_embedded

    def calculate_coordinates(self, images: np.ndarray) -> np.ndarray:
        """Calculating the coordinates of the uloaded images using opentnse t-SNE Method

        Args:
            images (np.ndarray): array of flat images

        Returns:
            np.ndarray: 2D coordinates of the supplied images
        """
        print("Calculation new coordinates")
        np_uploaded_images = np.array(images, dtype="float32")
        if np_uploaded_images.ndim == 1:
            np_uploaded_images = np_uploaded_images.reshape(1, -1)
        print("Reducing uploaded image")
        reduced_images = self.pca.transform(np_uploaded_images)
        uploaded_embedded = self.coordinates.transform(reduced_images)
        print(f"Uploaded Image Coordinates:\n{uploaded_embedded}")
        return uploaded_embedded

def get_instance() -> TSNE:
    """Return the current and preferably only instance of TSNE. If possible use this function to access the class methods of this class.

    Returns:
        TSNE: current instance of TSNE
    """
    return _instance

# Create the current and preferably only instance of TSNE
_instance = TSNE()
