# Start the server with this file!
from dotenv import load_dotenv
from api_package import db, app
import os

def main():
    # Check if .env file exists
    if not os.path.exists("./.env"):
        print("You need to specify environment variables in a .env file! See setup_dotenv.txt")
        exit(0)

    # Load .env file
    load_dotenv()

    db.main()
    app.main()

if __name__ == "__main__":
    main()