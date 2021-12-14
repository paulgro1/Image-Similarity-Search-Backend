# Start the server with this file!
from dotenv import load_dotenv
from os import path, environ, mkdir

def main():
    print(f"Executed {__file__}")
    the_path = path.dirname(__file__)
    dotenv_path = path.join(the_path, ".env")
    
    # Check if .env file exists
    if not path.exists(dotenv_path):
        exit("You need to specify environment variables in a .env file! See setup_dotenv.txt")

    # Load .env file
    load_dotenv(dotenv_path=dotenv_path)
    print("dotenv loaded")

    data_folder = environ.get("DATA_FOLDER")
    data_path = path.join(the_path, data_folder)

    # Check if data folder is specified, creating one if specified and not yet a directory
    if data_folder == None:
        exit("You need to supply a directory name for the dataset in your .env file!")
    elif not path.isdir(data_path):
        mkdir(data_path)
        exit(f"Created empty directory { data_folder } for dataset. Please insert dataset.")
    
    environ["DATA_PATH"] = data_path
    environ["SERVER_ROOT"] = the_path

    import api_package.app as app
    app.main()

if __name__ == "__main__":
    main()