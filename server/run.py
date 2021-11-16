# Start the server with this file!
from dotenv import load_dotenv
import os

def main():
    path = os.path.dirname(__file__)
    dotenv_path = os.path.join(path, ".env")
    
    # Check if .env file exists
    if not os.path.exists(dotenv_path):
        print("You need to specify environment variables in a .env file! See setup_dotenv.txt")
        exit(0)

    # Load .env file
    load_dotenv(dotenv_path=dotenv_path)

    data_folder = os.environ.get("DATA_FOLDER")
    data_path = os.path.join(path, data_folder)
    fullsize_path = os.path.join(data_path, os.environ.get("DATA_FULLSIZE_FOLDER"))
    thumbnails_path = os.path.join(data_path, os.environ.get("DATA_THUMBNAILS_FOLDER"))

    os.environ["DATA_PATH"] = data_path
    os.environ["FULLSIZE_PATH"] = fullsize_path
    os.environ["THUMBNAILS_PATH"] = thumbnails_path
    os.environ["SERVER_ROOT"] = path
    
    # Check if data folder is specified, creating one if specified and not yet a directory
    if data_folder == None:
        exit("You need to supply a directory name for the dataset in your .env file!")
    elif not os.path.isdir(data_path):
        os.mkdir(data_path)
        os.mkdir(fullsize_path)
        print(f"Created empty directory { data_folder } for dataset. Please insert dataset.")
        exit(0)
    
    if not os.path.isdir(thumbnails_path):
        os.mkdir(thumbnails_path)
        import api_package.process_images as img
        img.create_thumbnails()
    

    import api_package.app as app
    app.main()

if __name__ == "__main__":
    main()