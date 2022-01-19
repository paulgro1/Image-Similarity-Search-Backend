import numpy as np
from openTSNE import TSNE as openTSNE
from sklearn.decomposition._pca import PCA
from os import environ

if __name__ == "__main__":
    exit("Start via run.py!")

_instance = None

def get_instance():
    return _instance

class TSNE(object):

    def __init__(self):
        super().__init__()

        global _instance
        if _instance is None:
            _instance = self

    def initialize_coordinates(self, images):
        print("Initializing Coordinates")
        np_images = np.array(images, dtype="float32")
        if np_images.ndim == 1:
            np_images = np_images.reshape(1, -1)
        nr_of_samples = np_images.shape[0]
        dims = int(environ.get("REDUCE_IMAGE_TO_DIMS"))
        print(f"Reducing dimensions to {dims}")
        if dims > nr_of_samples:
            exit(f"Number of samples ({nr_of_samples}) needs to be greater or equal to the desired dimensions ({dims}) for PCA!")
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

    # Calculating the coordinates of the Images using opentnse t-SNE Method
    def calculate_coordinates(self, images):
        print("Calculation new coordinates")
        np_uploaded_images = np.array(images, dtype="float32")
        if np_uploaded_images.ndim == 1:
            np_uploaded_images = np_uploaded_images.reshape(1, -1)
        print("Reducing uploaded image")
        reduced_images = self.pca.transform(np_uploaded_images)
        uploaded_embedded = self.coordinates.transform(reduced_images)
        print(f"Uploaded Image Coordinates:\n{uploaded_embedded}")
        return uploaded_embedded  

_instance = TSNE()
