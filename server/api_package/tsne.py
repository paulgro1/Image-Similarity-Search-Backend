from sklearn.manifold import TSNE
import numpy as np

if __name__ == "__main__":
    exit("Start via run.py!")

# Calculating the coordinates of the Images using sklearn t-SNE Method
def calculate_coordinates(images, dummy=False):
    if dummy:
        # TODO remove dummy coordinates
        return np.random.rand(images.shape[0], 2) * 60000 - 30000
    np_images = np.array(images, dtype="float32")
    tsne = TSNE(n_components=2, perplexity=30.0, learning_rate=200.0, init='pca', verbose=1)
    images_embedded = tsne.fit_transform(np_images)
    return images_embedded

