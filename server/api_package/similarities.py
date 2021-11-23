import numpy as np

if __name__ == "__main__":
    exit("Start via run.py!")

class Similarities(object):

    def __init__(self):
        super().__init__()
 
    def get_similarities(D, k):
        similarities = []
        for d in range(len(D)):
            similarities.append([])
            for i in range(k):
                distance = np.take(D[d], i)
                similarity = 1/(1 + distance/1e+9)
                similarities[d].append(similarity)
                #print(f" {i+1}. Nearest Image Similarity : {similarity}")
        return similarities