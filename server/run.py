# Start the server with this file!
from dotenv import load_dotenv
import os

def main():
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    
    # Check if .env file exists
    if not os.path.exists(dotenv_path):
        print("You need to specify environment variables in a .env file! See setup_dotenv.txt")
        exit(0)

    # Load .env file
    load_dotenv(dotenv_path=dotenv_path)

    from api_package import db, app
    db.main()
    app.main()

if __name__ == "__main__":
    main()