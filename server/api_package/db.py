import pymongo
import os
import glob

if __name__ == "__main__":
    exit("Start via run.py!")


class Database(object):


    def __init__(self):
        super().__init__()
        # Client
        self._client = pymongo.MongoClient(os.environ.get("DATABASE_CLIENT"))
        # Database
        self._db = self._client[os.environ.get("DATABASE_NAME")]
        # Collections
        fs = os.environ.get("DATA_FULLSIZE_FOLDER")
        tn = os.environ.get("DATA_THUMBNAILS_FOLDER")
        self._collections = {
            fs: self._db[f"images_{fs}"],
            tn: self._db[f"images_{tn}"]
        }
        for c_name, collection in self._collections.items():
            self.initialize_collection(collection, c_name)
        

    def initialize_collection(self, collection, pathname):
        path = os.path.join(os.environ.get("DATA_FOLDER"), pathname, "*")
        images = [ { str(idx): url } for idx, url in enumerate(glob.iglob(pathname=path)) ]
        collection.insert_many(images)

def main():
    # TODO clear database / only add new entries
    Database()

