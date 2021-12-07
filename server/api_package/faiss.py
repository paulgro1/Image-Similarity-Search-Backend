from faiss import IndexFlatL2, IndexIVFFlat, METRIC_L2
import numpy as np

if __name__ == "__main__":
    exit("Start via run.py!")

class Faiss(object):
    FlatL2 = "IndexFlatL2"
    IVFFlat = "IndexIVFFlat"
    indices = {
        FlatL2: None,
        IVFFlat: None
    }

    def __init__(self):
        super().__init__()
        self.has_index = False
        print("Creating Faiss-Object")
        
    def _build_FlatL2(self, **kwargs):
        if not "d" in kwargs:
            return None
        d = kwargs["d"]
        index = IndexFlatL2(d)
        assert index.is_trained
        return index

    def _build_IVFFlat(self, images, **kwargs):
        if not "nlist" in kwargs or not "nprobe" in kwargs or not "d" in kwargs:
            print(f"Missing kwargs, need quantizer, nlist, nprobe, d: \n{kwargs}")
            return None
        nlist = kwargs["nlist"]
        nprobe = kwargs["nprobe"]
        d = kwargs["d"]
        quantizer = self._build_FlatL2(d=d)
        quantizer.add(images)
        index = IndexIVFFlat(quantizer, d, nlist, METRIC_L2)
        index.train(images)
        assert index.is_trained
        index.nprobe = nprobe
        return index

    def _set_index(self, key, index):
        if index != None:
            self.faiss_index = index
            self.has_index = True
            print(f"Set index {key}")
            return True
        return False

    def change_index(self, key):
        if key is None:
            print("No key given")
            return False
        if not key in self.indices.keys():
            print(f"Key {key} does not exist")
            return False
        index = self.indices[key]
        if index is None:
            print(f"Index with key {key} isn't build yet")
            return False
        return self._set_index(key, index)
    
    def build_index(self, key, training_filenames, training_images, **kwargs):
        if not key in self.indices.keys():
            print(f"Key {key} does not exist")
            return False
        print(f"Building index {key}")
        index = None
        if key == self.FlatL2:
            index = self._build_FlatL2(**kwargs)
        elif key == self.IVFFlat:
            index = self._build_IVFFlat(training_images, **kwargs)
        if index is None:
            return False
        self.indices[key] = index
        print("Building index complete")

        print("Initializing index")
        index.add(training_images)
        print("Amount of vectors in index:", index.ntotal)
        return True

    def search(self, images, k):
        if not self.has_index: 
            print("No index present!")
            return None
        images = np.array(images, dtype="float32")
        if images.ndim == 1:
            images = images[np.newaxis, ...]
        print(f"Searching index {type(self.faiss_index).__name__}")
        D, I = self.faiss_index.search(images, k)
        print(I)
        return D, I

    def get_index(self, key):
        if key in self.indices.keys():
            return self.indices[key]
        else:
            return None

    def get_all_indices_keys(self):
        return [ key for key in self.indices.keys() ]
            