"""Module supplies methods to convert distances between images into percentages"""
from numpy import ndarray

if __name__ == "__main__":
    exit("Start via run.py!")

def get_similarities_as_array(D: ndarray) -> ndarray:
    """Returns the percentages calculated from the distances between images as an array

    Args:
        D (np.ndarray): array of distances

    Returns:
        np.ndarray: array of percentages
    """
    similarities = 1 / (1 + D / 1e+9)
    return similarities

def get_similarities(D: ndarray) -> 'list[float]':
    """Returns the percentages calculated from the distances between images as a list

    Args:
        D (np.ndarray): array of distances

    Returns:
        list[float]: list of percentages
    """
    return get_similarities_as_array(D).tolist()
