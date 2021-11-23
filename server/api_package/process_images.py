from PIL import Image
from os import path, environ
from glob import iglob
import numpy as np

if __name__ == "__main__":
    exit("Start via run.py!")

def process_image(image):
    converted_image = Image.open(image).convert("RGB")
    resized_image = np.array(converted_image, dtype="float32").ravel()
    return resized_image

def load_images(the_path):
    filename_list = []
    image_list = []
    for image in iglob(path.join(the_path, "*")):
        filename = path.split(image)[-1]
        resized_image = process_image(image)
        filename_list.append(filename)
        image_list.append(resized_image)
    names = np.array(filename_list)
    images = np.array(image_list, dtype="float32")
    return names, images

def load_and_process_one_from_dataset(the_path):
    full_path = path.join(environ.get("DATA_PATH"), the_path)
    resized_image = process_image(full_path)
    return np.array(resized_image, dtype="float32")