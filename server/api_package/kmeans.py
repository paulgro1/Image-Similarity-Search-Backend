import numpy as np
from sklearn.cluster import KMeans

if __name__ == "__main__":
    exit("Start via run.py!")

_instance = None

def get_instance():
    return _instance

class KMeansWrapper(object):
    
    def __init__(self):
        super().__init__()
        print("Creating KMeans object")
        
        # Singletonesque pattern
        global _instance
        if _instance is None:
            _instance = self

    @property
    def cluster_centers(self) -> np.ndarray:
        if self.current_cluster is not None:
            return self.current_cluster.cluster_centers_

    @property
    def labels(self) -> np.ndarray:
        if self.current_cluster is not None:
            return self.current_cluster.labels_

    @property
    def coordinates(self):
        return self._coordinates

    @coordinates.setter
    def coordinates(self, value):
        self._coordinates = value

    @staticmethod
    def initialize(coordinates):
        global _instance
        _instance.coordinates = np.array(coordinates)
        print("Initialized kmeans")

    def cluster(self, num_clusters):
        print(f"Clustering with {num_clusters} centroids")
        num_clusters = min(max(num_clusters, 1), len(self.coordinates))
        kmeans = KMeans(
            num_clusters,
            verbose=1,
            random_state=123
        )
        kmeans.fit(self.coordinates)
        self.current_cluster = kmeans

    def predict(self, data):
        if self.current_cluster is None:
            print("No cluster initialized!")
            return None
        if data.ndim == 1:
            data = data.reshape(1, -1)
        labels = self.current_cluster.predict(data)
        return labels
        
_instance = KMeansWrapper()
