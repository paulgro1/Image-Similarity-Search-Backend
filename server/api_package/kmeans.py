"""Module is used to calculate cluster centers for given 2D points"""
import numpy as np
from sklearn.cluster import KMeans
from typing import Union, Tuple, Any

if __name__ == "__main__":
    exit("Start via run.py!")

# The instance of KMeansWrapper created on startup
_instance = None

class KMeansWrapper(object):
    """Class that wraps the sklearn KMeans class"""
    
    def __init__(self) -> None:
        """Initialize blank object, set object as _instance of module"""
        super().__init__()
        print("Creating KMeans object")
        
        # Singletonesque pattern
        global _instance
        if _instance is None:
            _instance = self

    @property
    def cluster_centers(self) -> 'Union[np.ndarray, None]':
        """Property of a KMeansWrapper instance, returning the cluster centers

        Returns:
            np.ndarray: Array containing the cluster centers 
        """
        if self.current_cluster is not None:
            return self.current_cluster.cluster_centers_

    @property
    def labels(self) -> 'Union[np.ndarray, None]':
        """Property of a KMeansWrapper instance, returning the labels of the clustered points

        Returns:
            np.ndarray: labels
        """
        if self.current_cluster is not None:
            return self.current_cluster.labels_

    @property
    def coordinates(self) -> 'Union[np.ndarray, None]':
        """Property of a KMeansWrapper instance, returning the coordinates the clusters are calculated on

        Returns:
            np.ndarray: coordinates
        """
        return self._coordinates

    @coordinates.setter
    def coordinates(self, value: np.ndarray) -> None:
        """Setter for the coordinates

        Args:
            value (np.ndarray): value to assign to property coordinates
        """
        self._coordinates = value

    @staticmethod
    def initialize(coordinates: np.ndarray) -> None:
        """Static method used to initialize blank object after startup

        Args:
            coordinates (np.ndarray): the coordinates
        """
        global _instance
        if _instance is None:
            _instance = KMeansWrapper()
        _instance.coordinates = np.array(coordinates)
        print("Initialized kmeans")

    def cluster(self, num_clusters: int) -> None:
        """Calculate num_clusters many cluster centers using KMeans. Access labels via api_package.kmeans.get_instance().labels,
        cluster centers via api_package.kmeans.get_instance().cluster_centers

        Args:
            num_clusters (int): Amount of cluster centers used in kmeans clustering
        """
        print(f"Clustering with {num_clusters} centroids")
        if not hasattr(self, "_coordinates"):
            exit("Please set the coordinates in initialize!")

        # Clamp amount of cluster centers 0 < num_clusters < len(self.coordinates)
        num_clusters = min(max(num_clusters, 1), len(self.coordinates))
        kmeans = KMeans(
            num_clusters,
            verbose=1,
            random_state=123
        )
        kmeans.fit(self.coordinates)
        self.current_cluster = kmeans

    def predict(self, data: np.ndarray) -> np.ndarray:
        """Predict the cluster centers of the images supplied in data

        Args:
            data (np.ndarray): array of 2D points

        Returns:
            np.ndarray: array of cluster center labels
        """
        if self.current_cluster is None:
            print("No cluster initialized!")
            return None
        if data.ndim == 1:
            data = data.reshape(1, -1)
        labels = self.current_cluster.predict(data)
        return labels

def get_instance() -> KMeansWrapper:
    """Return the current and preferably only instance of KMeansWrapper. If possible use this function to access the class methods of this class.

    Returns:
        KMeansWrapper: current instance of KMeansWrapper
    """
    return _instance

# Create the current and preferably only instance of KMeansWrapper
_instance = KMeansWrapper()
