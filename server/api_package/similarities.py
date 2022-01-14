
if __name__ == "__main__":
    exit("Start via run.py!")

def get_similarities_as_array(D):
    similarities = 1 / (1 + D / 1e+9)
    return similarities

def get_similarities(D):
    return get_similarities_as_array(D).tolist()
