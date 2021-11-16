from PIL import Image
import os
import glob

if __name__ == "__main__":
    exit("Start via run.py!")

thumbnail_size = (128, 128)

def create_thumbnails():
    fullsize_path = os.environ.get("FULLSIZE_PATH")
    thumbnails_path = os.environ.get("THUMBNAILS_PATH")
    for image in glob.iglob(os.path.join(fullsize_path, "*")):
        filename = os.path.split(image)[-1]
        with Image.open(image) as img:
            img.thumbnail(thumbnail_size)
            img.save(os.path.join(thumbnails_path, filename))
