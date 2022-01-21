"""Module supplies the Faiss class, which wraps the fiass module"""
from faiss import IndexFlatL2, IndexIVFFlat, METRIC_L2
import numpy as np
from typing import Tuple, Union, Any

if __name__ == "__main__":
    exit("Start via run.py!")

# The instance of Faiss created on startup
_instance = None


class Faiss(object):
    """Class wrapping the faiss module"""
    FlatL2 = "IndexFlatL2"
    IVFFlat = "IndexIVFFlat"
    indices = {
        FlatL2: None,
        IVFFlat: None
    }

    def __init__(self) -> None:
        """Initialize blank object, set object as _instance of module"""
        super().__init__()
        
        self.has_index = False

        # Singletonesque pattern
        print("Creating Faiss-Object")
        global _instance
        if _instance is None:
            _instance = self
        
    def _build_FlatL2(self, **kwargs: 'dict[str, Any]') -> 'Union[Any, None]':
        """Initialize a faiss FlatIndexL2

        Args:
            kwargs (dict): should contain d (int), the dimension of the flat data

        Returns:
            Any: faiss index
        """
        if not "d" in kwargs:
            return None
        d = kwargs["d"]
        index = IndexFlatL2(d)
        assert index.is_trained
        return index

    def _build_IVFFlat(self, images: np.ndarray, **kwargs: 'dict[str, Any]') -> 'Union[Any, None]':
        """Initialize a faiss IndexIVFFlat

        Args:
            images (np.array): flat images to train the index on
            kwargs (dict): should contain nlist (int), the amount of centroids, nprobe (int), amount of probes per iteration,
            d (int), the dimension of the flat data

        Returns:
            Any: faiss index
        """
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

    def _set_index(self, key: str, index: Any) -> bool:
        """Set a faiss index, which can be used for future searches

        Args:
            key (str): key, meaning identifier, associated with the faiss index. Keys are class variables of this class
            index (Any): the faiss index

        Returns:
            bool: True if successful, False if an error occured
        """
        if index != None:
            self.faiss_index = index
            self.has_index = True
            print(f"Set index {key}")
            return True
        return False

    def change_index(self, key: str) -> bool:
        """Change the current index to the faiss index associated with the key

        Args:
            key (str): key, meaning identifier, associated with the faiss index. Keys are class variables of this class

        Returns:
            bool: True if successful, False if an error occured
        """
        if key is None:
            print("No key given")
            return False
        if not key in self.indices.keys():
            print(f"Key {key} does not exist")
            return False
        index = self.indices[key]
        if index is None:
            print(f"Index {key} load failed")
            return False
        return self._set_index(key, index)
    
    def build_index(self, key: str, training_filenames: np.ndarray, training_images: np.ndarray, **kwargs: 'dict[str, Any]') -> bool:
        """Convenience method used to build faiss index associated with the key

        Args:
            key (str): key, meaning identifier, associated with the faiss index. Keys are class variables of this class
            training_filenames (np.ndarray): the filenames of the training images
            training_images (np.ndarray): the flat training images
            kwargs (dict): should contain all keyworded arguments needed for building the faiss index

        Returns:
            bool: True if build was successful, False if key is unknown or a different error occured
        """
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

    def search(self, images: np.ndarray, k: int) -> 'Union[Tuple[np.ndarray, np.ndarray], None]':
        """Returns the k nearest neighbours and distances of the flat images in the images array using the current faiss index

        Args:
            images (np.ndarray): array containing the flat images, whose neighbours shall be found
            k (int): value indicating, how many neighbours shall be found. Should be 0 < k < Faiss.get_instance().faiss_index.ntotal

        Returns:
            np.array: Distances to the nearest neighbours
            np.array: Indices of the nearest neighbours
        """
        if not self.has_index: 
            print("No index present!")
            return None
        images = np.array(images, dtype="float32")
        if images.ndim == 1:
            images = images[np.newaxis, ...]
        print(f"Searching index {type(self.faiss_index).__name__}")
        D, I = self.faiss_index.search(images, k)
        return D, I
    
    def get_all_indices_keys(self) -> 'list[str]':
        """Get keys for all available faiss indices

        Returns:
            list (str): list of keys
        """
        return [ key for key in self.indices.keys() ]

def get_instance() -> Faiss:
    """Return the current and preferably only instance of Faiss. If possible use this function to access the class methods of this class.

    Returns:
        Faiss: current instance of Faiss
    """
    return _instance

# Create the current and preferably only instance of Faiss
_instance = Faiss()
