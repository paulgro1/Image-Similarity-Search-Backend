from pymongo import MongoClient, UpdateOne
from os import path, environ
from glob import iglob, glob
from gridfs import GridFS
from PIL import Image
from io import BytesIO
import numpy as np
import pickle
from api_package.helper import allowed_file
from faiss import serialize_index, deserialize_index

if __name__ == "__main__":
    exit("Start via run.py!")

class Database(object):

    def __init__(self):
        super().__init__()
        print("Creating Database")
        # Client
        self._client = MongoClient(environ.get("DATABASE_CLIENT"))
        # Database
        self._db = self._client[environ.get("DATABASE_NAME")]
        
        # GridFS for image storage
        self._gridfs = GridFS(self._db)
        self.id_projection = { "id": True }
        self.fullsize_projection = { "id": True, "filename": True, "path": True }
        self.thumbnail_projection = { "id": True, "filename": True, "thumbnail": True }

    def reset_col(self, col_name):
        col = self._db[col_name]
        col.drop()
        col.drop_indexes()

    def count_documents_in_collection(self, options={}):
        return self.col.count_documents(options)

    def initialize(self, flat_filenames, coordinates, labels):
        coordinates = np.concatenate((flat_filenames[..., np.newaxis], coordinates, labels[..., np.newaxis]), axis=1)
        print("Initializing Database")
        self.reset_col("images")
        self.reset_col("fs.files")
        self.reset_col("fs.chunks")
        # self.reset_col("faiss")

        thumbnail_width = environ.get("THUMBNAIL_WIDTH")
        thumbnail_height = environ.get("THUMBNAIL_HEIGHT")
        if thumbnail_width is None or thumbnail_height is None:
            exit("Please update your .env file! Missing thumbnail sizes")
        thumbnail_size = (int(thumbnail_width), int(thumbnail_height))
        actual_thumbnail_size = None
        images = []
        base_path = environ.get("DATA_PATH")
        for idx, item in enumerate(coordinates):
            f = path.join(base_path, item[0])
            t_id = None
            filename = path.split(f)[-1]
            if allowed_file(filename):
                with Image.open(f) as img:
                    img.thumbnail(thumbnail_size)
                    if actual_thumbnail_size is None:
                        actual_thumbnail_size = img.size
                    with BytesIO() as output:
                        img.save(output, format=img.format)
                        content = output.getvalue()
                    only_filename, extension = path.splitext(filename)
                    t_id = self._gridfs.put(
                        content, 
                        content_type=Image.MIME[img.format], 
                        filename=f"{only_filename}_thumbnail{extension}", 
                        metadata="thumbnail", 
                        id=idx
                        )
                x = item[1]
                y = item[2]
                cluster_center = item[3]
                image = {
                    "id": idx,
                    "filename": filename,
                    "path": f,
                    "thumbnail": t_id,
                    "x": x,
                    "y": y,
                    "cluster_center": cluster_center
                }
                images.append(image)
        self.col = self._db["images"]
        self.col.insert_many(images)
        environ["ACTUAL_THUMBNAIL_WIDTH"] = str(actual_thumbnail_size[0])
        environ["ACTUAL_THUMBNAIL_HEIGHT"] = str(actual_thumbnail_size[1])
        print("Database initialized")

    """
    def save_index(self, key, index):
        print(f"saving index {key}")
        serialized = serialize_index(index)
        dump = pickle.dumps(serialized)
        the_id = self._gridfs.put(dump, filename=key, metadata="faiss")
        the_obj = {
            "index_id": the_id,
            "key": key
        }
        self._db["faiss"].insert_one(the_obj)
        self._db.command({"planCacheClear" : "faiss"})
    
    def load_index(self, key):
        print(f"loading index {key}")
        the_col = self._db["faiss"]
        assert the_col.count_documents({}) != 0
        the_id = the_col.find_one({ "key": key })["index_id"]
        self._db.command({"planCacheClear" : "faiss"})
        dump = self._gridfs.find({ "_id": the_id })[0].read()
        index = deserialize_index(pickle.loads(dump))
        return index
    """
    
    def get_one(self, filter, projection):
        if filter == None:
            return None
        return self.col.find_one(filter, projection=projection)

    def get_one_by_id(self, id, projection):
        if id != None and self.count_documents_in_collection() > 0:
            return self.get_one({"id": id}, projection)
        return None

    def is_id_in_database(self, id):
        return not self.get_one_by_id(id, self.id_projection) is None
        
    def get_one_fullsize_by_id(self, id):
        return self.get_one_by_id(id, self.fullsize_projection)

    def get_multiple(self, filter={}, projection={ "id": True, "filename": True, "path": True, "thumbnail": True }):
        as_list = list(self.col.find(filter=filter, projection=projection))
        for d in as_list:
            del d["_id"]
        return as_list

    def get_all_coordinates_as_array(self) -> np.ndarray:
        coords = self.col.find({}, { "x": True, "y": True })
        lines = []
        for line in coords:
            lines.append([line["x"], line["y"]])
        return np.array(lines, dtype="float64")

    def get_all(self, projection={ "id": True, "filename": True, "path": True, "thumbnail": True }):
        return self.get_multiple({}, projection)

    def get_all_ids(self):
        if self.count_documents_in_collection() > 0:
            return self.get_all(self.id_projection)
        return None

    def get_all_fullsize(self):
        if self.count_documents_in_collection() > 0:
            return self.get_all(self.fullsize_projection)
        return None

    def get_multiple_by_id(self, ids, projection):
        if ids != None and len(ids) != 0 and self.count_documents_in_collection() > 0:
            filter = {"id": {"$in" : ids}}
            return self.get_multiple(filter, projection)
        return None

    def are_all_ids_in_database(self, ids):
        if ids is None:
            return False, "no ids given!"
        if not isinstance(ids, list):
            ids = [ids]
        result = self.get_multiple_by_id(ids, { "id": True })
        result_list = list(result)
        success = len(result_list) == len(ids)
        if success:
            return True, None
        else:
            result_list = [ int(x["id"]) for x in result_list ]
            # See https://stackoverflow.com/questions/3462143/get-difference-between-two-lists
            not_present = list(set(ids) - set(result_list))
            return False, not_present

    def get_multiple_fullsize_by_id(self, ids):
        return self.get_multiple_by_id(ids, self.fullsize_projection)

    def get_thumbnail_fs_id(self, picture_id):
        return self.get_one_by_id(picture_id, { "thumbnail": True })["thumbnail"]

    def get_one_thumbnail_by_id(self, entry_id):
        id = self.get_thumbnail_fs_id(entry_id)
        return self._gridfs.get(id)
        
    def get_all_thumbnails(self):
        if self.count_documents_in_collection() > 0:
            result = self._gridfs.find({ "metadata" : "thumbnail" })
            if not result is None:
                return [ x for x in result ]    
            return None 
        return None

    def get_multiple_thumbnails_by_id(self, ids):
        if self.count_documents_in_collection() > 0:
            fs_ids = self.get_multiple_by_id(ids, { "thumbnail": True })
            fs_ids = [ x["thumbnail"] for x in fs_ids ]
            result = self._gridfs.find({ "_id": {"$in" : fs_ids}, "metadata": "thumbnail" })
            if not result is None:
                return [ x for x in result ]

    def get_coordinates(self, id):
        result = self.get_one_by_id(id, { "x": True, "y": True})
        if not result is None:
            x = result["x"]
            y = result["y"]
            return (x, y)
        return None

    def get_metadata(self, id):
        result = self.get_one_by_id(id, { "id": True, "filename": True, "x": True, "y": True, "cluster_center": True})
        if not result is None:
            return {
                "id": result["id"],
                "filename": result["filename"],
                "image_size": {
                    "width": environ.get("FULLSIZE_WIDTH"),
                    "height": environ.get("FULLSIZE_HEIGHT")
                },
                "thumbnail_size": {
                    "width": environ.get("ACTUAL_THUMBNAIL_WIDTH"),
                    "height": environ.get("ACTUAL_THUMBNAIL_HEIGHT")
                },    
                "position": (result["x"], result["y"]),
                "cluster_center": result["cluster_center"]
            }
        return None
    
    def get_multiple_metadata(self, ids):
        result = self.get_multiple_by_id(ids, { "id": True, "filename": True, "x": True, "y": True, "cluster_center": True})
        if not result is None:
            return [ { 
                "id": x["id"], 
                "filename": x["filename"], 
                "position": (x["x"], x["y"]),
                "image_size": {
                    "width": environ.get("FULLSIZE_WIDTH"),
                    "height": environ.get("FULLSIZE_HEIGHT")
                },
                "thumbnail_size": {
                    "width": environ.get("ACTUAL_THUMBNAIL_WIDTH"),
                    "height": environ.get("ACTUAL_THUMBNAIL_HEIGHT")
                },
                "cluster_center": x["cluster_center"] 
            } for x in result ]
        return None

    def get_all_metadata(self):
        result = self.get_all({ "id": True, "filename": True, "x": True, "y": True, "cluster_center": True })
        if not result is None:
            return [ { 
                "id": x["id"], 
                "filename": x["filename"], 
                "position": (x["x"], x["y"]),
                "image_size": {
                    "width": environ.get("FULLSIZE_WIDTH"),
                    "height": environ.get("FULLSIZE_HEIGHT")
                },
                "thumbnail_size": {
                    "width": environ.get("ACTUAL_THUMBNAIL_WIDTH"),
                    "height": environ.get("ACTUAL_THUMBNAIL_HEIGHT")
                },
                "cluster_center": x["cluster_center"] 
            } for x in result ]
        return None

    def get_one_filename(self, id):
        return self.get_one_by_id(id, { "filename": True })["filename"]

    def ids_to_filenames(self, ids):
        if ids is None:
            return None
        if not isinstance(ids, np.ndarray):
            return None
        if ids.ndim == 1:
            ids = ids.reshape(1, -1)
        filenames = []
        for row in ids:
            c_filenames = []
            for item in row:
                c_filenames.append(self.get_one_filename(int(item)))
            filenames.append(c_filenames)
        return filenames

    def update_labels(self, labels):
        updateOps = [
            UpdateOne({ "id": idx }, { "$set": { "cluster_center": int(item) }}) for idx, item in enumerate(labels)
        ]
        self.col.bulk_write(updateOps)

    def get_one_label(self, id):
        return self.get_metadata(id)["cluster_center"]