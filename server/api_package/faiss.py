from faiss import IndexFlatL2
import numpy as np

if __name__ == "__main__":
    exit("Start via run.py!")

class Faiss(object):
    FlatL2 = "IndexFlatL2"


    def __init__(self, training_filenames, training_images):
        super().__init__()
        print("Creating Faiss-Object")
        self.has_index = False
        self.is_trained = False
        self.training_filenames = training_filenames
        self.training_images = training_images
    
    def _build_FlatL2(self, **kwargs):
        if not "d" in kwargs:
            return
        d = kwargs["d"]
        index = IndexFlatL2(d)
        assert index.is_trained
        return index

    def _set_index(self, index):
        if index != None and not self.has_index:
            self.faiss_index = index
            self.has_index = True
            
    
    def index(self, key, **kwargs):
        print(f"Building index {key}")
        index = None
        if key == self.FlatL2:
            index = self._build_FlatL2(**kwargs)
        self._set_index(index)
        print("Building index complete")


    def initialize_index(self):
        if not self.has_index:
            return
        self.faiss_index.add(self.training_images)
        print("Amount of vectors in index:", self.faiss_index.ntotal)
        self.is_trained = True


    def search(self, images, k):
        images = np.array(images, dtype="float32")
        if images.ndim == 1:
            images = images[np.newaxis, ...]
        D, I = self.faiss_index.search(images, k)
        return D, I