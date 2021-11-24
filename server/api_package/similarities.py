
if __name__ == "__main__":
    exit("Start via run.py!")

def get_similarities(D):
    similarities = 1 / (1 + D / 1e+9)
    return similarities.tolist()
