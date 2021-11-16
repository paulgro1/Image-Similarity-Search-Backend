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

    def reset_col(self, col_name):
        col = self._db[col_name]
        col.drop()
        col.drop_indexes()

    def count_documents_in_collection(self, options={}):
        return self.col.count_documents(options)

    def initialize(self):
        self.reset_col("images")
        f_path = os.path.join(os.environ.get("FULLSIZE_PATH"), "*")
        fullsize_filenames = [ (os.path.split(x)[-1], x) for x in glob.iglob(pathname=f_path) ]
        t_path = os.path.join(os.environ.get("THUMBNAILS_PATH"), "*")
        thumbnails_filenames = [ (os.path.split(x)[-1], x) for x in glob.iglob(pathname=t_path) ]

        fullsize_filenames.sort(key=lambda x: x[0])
        thumbnails_filenames.sort(key=lambda x: x[0])

        f_idx = 0
        t_idx = 0
        true_idx = 0
        images = []
        while f_idx < len(fullsize_filenames) and t_idx < len(thumbnails_filenames):
            f_file = fullsize_filenames[f_idx]
            t_file = thumbnails_filenames[t_idx]
            if f_file[0] != t_file[0]:
                if f_file[0] < t_file[0]:
                    f_idx += 1
                else:
                    t_idx += 1
                continue
            image = {
                "id": true_idx,
                "filename": f_file[0],
                "fullsize": f_file[1],
                "thumbnail": t_file[1]
            }
            images.append(image)
            f_idx += 1
            t_idx += 1
            true_idx += 1

        self.col = self._db["images"]
        self.col.insert_many(images)
        self.id_projection = { "id": True }
        self.fullsize_projection = { "id": True, "filename": True, "fullsize": True }
        self.thumbnail_projection = { "id": True, "filename": True, "thumbnail": True }

    def get_one(self, filter, projection):
        if filter == None:
            return None
        return self.col.find_one(filter, projection=projection)

    def get_one_by_id(self, id, projection):
        if id != None and self.count_documents_in_collection() > 0:
            return self.get_one({"id": id}, projection)
        return None

    def is_id_in_database(self, id):
        return self.get_one_by_id(id, self.id_projection) != None
        
    def get_one_fullsize_by_id(self, id):
        return self.get_one_by_id(id, self.fullsize_projection)

    def get_one_thumbnail_by_id(self, id):
        return self.get_one_by_id(id, self.thumbnail_projection)

    def get_multiple(self, filter={}, projection={ "id": True, "filename": True, "fullsize": True, "thumbnail": True }):
        as_list = list(self.col.find(filter=filter, projection=projection))
        for d in as_list:
            del d["_id"]
        return as_list

    def get_all(self, projection={ "id": True, "filename": True, "fullsize": True, "thumbnail": True }):
        return self.get_multiple({}, projection)

    def get_all_ids(self):
        if self.count_documents_in_collection() > 0:
            return self.get_all(self.id_projection)
        return None

    def get_all_fullsize(self):
        if self.count_documents_in_collection() > 0:
            return self.get_all(self.fullsize_projection)
        return None

    def get_all_thumbnails(self):
        if self.count_documents_in_collection() > 0:
            return self.get_all(self.thumbnail_projection)
        return None

    def get_multiple_by_id(self, ids, projection):
        if ids != None and len(ids) != 0 and self.count_documents_in_collection() > 0:
            filter = {"id": {"$in" : ids}}
            return self.get_multiple(filter, projection)
        return None

    def get_multiple_fullsize_by_id(self, ids):
        return self.get_multiple_by_id(ids, self.fullsize_projection)

    def get_multiple_thumbnails_by_id(self, ids):
        return self.get_multiple_by_id(ids, self.thumbnail_projection)

