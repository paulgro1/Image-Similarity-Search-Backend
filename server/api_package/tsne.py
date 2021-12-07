import numpy as np
from openTSNE import TSNE as openTSNE
from sklearn.decomposition._pca import PCA
from os import environ

if __name__ == "__main__":
    exit("Start via run.py!")

class TSNE(object):

    def initialize_coordinates(self, images):
        print("Initializing Coordinates")
        np_images = np.array(images, dtype="float32")
        if np_images.ndim == 1:
            np_images = np_images.reshape(1, -1)
        dims = int(environ.get("REDUCE_IMAGE_TO_DIMS"))
        print(f"Reducing dimensions to {dims}")
        self.pca = PCA(n_components=dims)
        reduced_images = self.pca.fit_transform(np_images)
        tsne = openTSNE(initialization="pca", perplexity=40, metric="euclidean", n_jobs=-1, verbose=True)
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