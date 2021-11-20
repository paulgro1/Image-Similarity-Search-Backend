from PIL import Image
import os
import glob
import numpy as np

if __name__ == "__main__":
    exit("Start via run.py!")

def process_image(image):
    converted_image = Image.open(image).convert("RGB")
    resized_image = np.array(converted_image, dtype="float32").ravel()
    return resized_image

def load_images(path):
    filename_list = []
    image_list = []
    for image in glob.iglob(os.path.join(path, "*")):
        filename = os.path.split(image)[-1]
        resized_image = process_image(image)
        filename_list.append(filename)
        image_list.append(resized_image)
    names = np.array(filename_list)
    images = np.array(image_list, dtype="float32")
    return names, images