# See https://github.com/facebookresearch/faiss/wiki/Getting-started
import numpy as np
import glob
import os
from PIL import Image
import time
from dotenv import load_dotenv
from sklearn.manifold import TSNE
from matplotlib import pyplot as plt
import seaborn as sns

root_path = os.path.dirname(os.path.dirname(__file__))
dotenv_path = os.path.join(root_path, ".env")
load_dotenv(dotenv_path=dotenv_path)

def load_images(path):
    filename_list = []
    image_list = []
    for image in glob.iglob(os.path.join(path, "*")):
        filename = os.path.split(image)[-1]
        converted_image = Image.open(image).convert("RGB")
        resized_image = np.array(converted_image, dtype="float32").ravel()
        filename_list.append(filename)
        image_list.append(resized_image)
    database = np.array(image_list, dtype="float32")
    return filename_list, database

# Calculating the coordinates of the Images using sklearn t-SNE Method, visualisation only for testing with seaborn scatter chart 
def tsne(images):
    np_images = np.array(images, dtype="float32")
    tsne = TSNE(n_components=2, perplexity=30.0, learning_rate=200.0, init='pca')
    images_embedded = tsne.fit_transform(np_images)
    for i in range(len(images)):
        print(f"Image: {i} Coordinates: {images_embedded[i]}")
    sns.set(rc={'figure.figsize':(11.7,8.27)})
    sns.scatterplot(x = images_embedded[:,0], y = images_embedded[:,1], legend='full')
    plt.show()
    return images_embedded

def main(show_images, k):
    base_path = os.path.dirname(__file__)

    training_path = os.path.join(root_path, os.environ.get("DATA_FOLDER"), os.environ.get("DATA_FULLSIZE_FOLDER"))
    training_filenames, training_images = load_images(training_path)

    query_path = os.path.join(base_path, "query")
    query_filenames, query_images = load_images(query_path)

    assert training_images.shape[1] == query_images.shape[1]

    import faiss                   # make faiss available
    index = faiss.IndexFlatL2(training_images[0].shape[0])   # build the index
    print("Trained?", index.is_trained)
    index.add(training_images)                  # add vectors to the index
    print("Amount of vectors in index:", index.ntotal)

    D, I = index.search(query_images, k)
    
    for idx, nearest in enumerate(I):
        query_filename = query_filenames[int(idx)]
        print(f"{idx+1}. Query Image: {query_filename}")
        for jdx in range(k):
            nearest_img = int(nearest[jdx])
            training_filename = training_filenames[nearest_img]
            print(f"{jdx+1}. Nearest Image: {training_filename}")
        if show_images:
            Image.open(os.path.join(query_path, query_filename)).show()
            Image.open(os.path.join(training_path, training_filename)).show()
            time.sleep(5)
    tsne(training_images)
    return

if __name__ == "__main__":
    show_images = False # with k = 1 !
    k = 10 # k nearest neighbours
    main(show_images, k)
