"""Start the backend server by executing this file!"""
from dotenv import load_dotenv
from typing import NoReturn, Union
from os import path, environ, mkdir

def main() -> 'Union[None, NoReturn]':
    """Only way to reliably start the backend server, usually called by executing the file run.py"""
    print(f"Executed {__file__}")
    the_path = path.dirname(__file__)
    dotenv_path = path.join(the_path, ".env")
    
    # Check if .env file exists
    if not path.exists(dotenv_path):
        exit("You need to specify environment variables in a .env file! See INSTALL.md")

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

    # Starting the server via app.py
    import api_package.app as app
    app.main()

if __name__ == "__main__":
    main()