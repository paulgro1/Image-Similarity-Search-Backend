import numpy as np
from openTSNE import TSNE as openTSNE

class TSNE(object):
    
    def __init__(self):
        self.coordinates = []

    # Calculating the coordinates of the Images using opentnse t-SNE Method
    def calculate_coordinates(self, images, isuploaded, dummy):
        if dummy:
            # TODO remove dummy coordinates
            return np.random.rand(images.shape[0], 2) * 60000 - 30000
        if not isuploaded:
            np_images = np.array(images, dtype="float32")
            tsne = openTSNE(initialization="pca", perplexity=30, metric="euclidean", n_jobs=8, verbose=True)
            images_embedded = tsne.fit(np_images)
            self.coordinates = images_embedded
            return images_embedded  

        else:
            np_uploaded_images = np.array(images, dtype="float32")
            uploaded_embedded = self.coordinates.transform(np_uploaded_images)
            print(f"Uploaded Image Coordinates: {uploaded_embedded}")
            return uploaded_embedded  