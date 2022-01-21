"""Module containing Database class, a wrapper for a pymongo instance"""
from gridfs import GridFS
from io import BytesIO
import numpy as np
from os import path, environ
from pandas import DataFrame
from PIL import Image
from pymongo import MongoClient, UpdateOne, ASCENDING
from typing import Any, Union, Tuple, Literal

from api_package.helper import allowed_file

if __name__ == "__main__":
    exit("Start via run.py!")

# The instance of Database created on startup
_instance = None


class Database(object):
    """Class wrapping the pymongo MongoDB connection, supplying convenience methods for easier access"""
    
    def __init__(self) -> None:
        """Initailize blank object, establish connection to MongoDB database and setup GridFS. Set object as _instance of module"""
        super().__init__()
        print("Creating Database")
        # Client
        self._client = MongoClient(environ.get("DATABASE_CLIENT"))
        # Database
        self._db = self._client[environ.get("DATABASE_NAME")]
        
        # GridFS for image storage
        self._gridfs = GridFS(self._db)

        # Projections
        self.id_projection = { "id": True }
        self.fullsize_projection = { "id": True, "filename": True, "path": True }
        self.thumbnail_projection = { "id": True, "filename": True, "thumbnail": True }
        self.possible_search_parameters = ["_id", "id", "filename", "path", "thumnbnail", "x", "y", "cluster_center"]

        # Casting for each column
        self.type_reg = {
            "id": int,
            "filename": str,
            "path": str,
            "x": float,
            "y": float,
            "thumbnail": lambda identity: identity,
            "cluster_center": int
        }

        # Singletonesque pattern
        global _instance
        if _instance is None:
            _instance = self

    def reset_col(self, col_name: str) -> None:
        """Reset, aka drop a MongoDB collection

        Args:
            col_name (str): String specifiying which collection to drip
        """
        col = self._db[col_name]
        if col:
            col.drop()
            col.drop_indexes()

    def count_documents_in_collection(self, filter: dict={}) -> int:
        """Count the documents in the MongoDB images collection

        Args:
            filter (dict, optional): args to filter the counted elements. Defaults to {}.

        Returns:
            int: amount of documents in the image collection
        """
        if self.col:
            return self.col.count_documents(filter)
        else:
            return -1

    def is_db_empty(self) -> bool:
        """Checks if the MongoDB image collection is empty

        Returns:
            bool: True if empty, False if at least one document is in collection
        """
        return self.count_documents_in_collection() <= 0

    def initialize(self, flat_filenames: np.ndarray, coordinates: np.ndarray, labels: np.ndarray) -> None:
        """Call this method to initialize the blank object created on load via get_instance().
        Fills MongoDB image collection and generates a thumbnail for each image.

        Args:
            flat_filenames (np.ndarray): the filenames of the images in the dataset
            coordinates (np.ndarray): calculated 2D coordinates of the images in the dataset
            labels (np.ndarray): generated labels aka corresponding cluster centers of the images in the dataset
        """        
        # Concatenate parameters for accessibility
        data = np.concatenate((flat_filenames[..., np.newaxis], coordinates, labels[..., np.newaxis]), axis=1)
        
        print("Initializing Database")
        # Reset all collections
        self.reset_col("images")
        self.reset_col("fs.files")
        self.reset_col("fs.chunks")
        self.reset_col("sessions")
        
        # Get maximum size of thumbnails
        thumbnail_width = environ.get("THUMBNAIL_WIDTH")
        thumbnail_height = environ.get("THUMBNAIL_HEIGHT")
        if thumbnail_width is None or thumbnail_height is None:
            exit("Please update your .env file! Missing thumbnail sizes")
        thumbnail_size = (int(thumbnail_width), int(thumbnail_height))
        
        # Iterate over all rows of data, inserting values for valid images into database
        actual_thumbnail_size = None
        images = []
        base_path = environ.get("DATA_PATH")
        for idx, item in enumerate(data):
            f = path.join(base_path, item[0])
            t_id = None
            filename = path.split(f)[-1]
            if allowed_file(filename):
                # Generate thumbnail
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

                # Setup document to insert
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

        # Insert into images collection
        self.col = self._db["images"]
        self.col.insert_many(images)
        self.col.create_index([("id", ASCENDING)])

        self.next_id = images[-1]["id"] + 1
        environ["ACTUAL_THUMBNAIL_WIDTH"] = str(actual_thumbnail_size[0])
        environ["ACTUAL_THUMBNAIL_HEIGHT"] = str(actual_thumbnail_size[1])
        print("Database initialized")

    def is_session_key_in_db(self, key: bytes) -> bool:
        """Check if api session key is already present in database

        Args:
            key (bytes): key to assess

        Returns:
            bool: True if already present, False if not in database
        """
        if key is None:
            return False
        result = self._db["sessions"].find_one({"key": key})
        return result is not None

    def insert_session_key(self, key: bytes) -> None:
        """Insert a new api session key into the database, setting next id (value) to the next valid id (self.next_id)

        Args:
            key (bytes): key to insert
        """
        self._db["sessions"].insert_one({ "key": key, "value": self.next_id })

    def get_next_ids(self, key: bytes, amount: int=1) -> 'Union[list[int], None]':
        """Get the next consecutive ids after the last valid id for the given key

        Args:
            key (bytes): key for which the next ids shall be returned
            amount (int): amount of new ids to be returned. Defaults to 1.

        Returns:
            list (int): New ids
        """
        if amount < 1:
            return None
        if key is not None:
            current_next_value = self._db["sessions"].find_one_and_update(
                { "key": key }, { "$inc": { "value": amount } }
            )
            if current_next_value is not None and "value" in current_next_value:
                current_next_value = int(current_next_value["value"])
            else:
                current_next_value = self.next_id
        else:
            current_next_value = self.next_id
        if amount == 1:
            return [current_next_value]
        else:
            return list(range(current_next_value, current_next_value + amount))
    
    def get_one(self, filter: dict, projection: dict) -> 'Union[Any, None]':
        """Return one document from the image collection

        Args:
            filter (dict): dict to filter documents by
            projection (dict): dict to filter attributes of returned documents by

        Returns:
            Any: document
        """        
        if filter == None:
            return None
        return self.col.find_one(filter, projection=projection)

    def get_one_by_id(self, id: int, projection: dict) -> 'Union[Any, None]':
        """Return one document from the image collection specified by the id

        Args:
            id (int): id of the image
            projection (dict): dict to filter attributes of returned documents by

        Returns:
            Any: document
        """
        if id != None and not self.is_db_empty():
            return self.get_one({"id": id}, projection)
        return None

    def is_id_in_database(self, id: int) -> bool:
        """Checks if id is present in image collection

        Args:
            id (int): id of image to assess

        Returns:
            bool: True if present, False if not in database
        """
        return not self.get_one_by_id(id, self.id_projection) is None
        
    def get_one_fullsize_by_id(self, id: int) -> 'Union[Any, None]':
        """Return one fulllsize image specified by given id

        Args:
            id (int): id of image to be found

        Returns:
            Any: the found document
        """
        return self.get_one_by_id(id, self.fullsize_projection)

    def get_multiple(self, filter: dict={}, projection: dict={ "id": True, "filename": True, "path": True, "thumbnail": True }) -> 'list[Any]':
        """Returns multiple documents specified by parameters

        Args:
            filter (dict): dict to filter documents by
            projection (dict): dict to filter attributes of returned documents by. Defaults to { "id": True, "filename": True, "path": True, "thumbnail": True }

        Returns:
            list (Any): list of found documents
        """
        as_list = list(self.col.find(filter=filter, projection=projection))
        for d in as_list:
            del d["_id"]
        return as_list

    def get_all_coordinates_as_array(self) -> np.ndarray:
        """Returns all coordinates in image collection

        Returns:
            np.ndarray: All coordinates as array
        """
        coords = self.col.find({}, { "x": True, "y": True })
        lines = []
        for line in coords:
            lines.append([line["x"], line["y"]])
        return np.array(lines, dtype="float64")

    def get_all(self, projection: dict={ "id": True, "filename": True, "path": True, "thumbnail": True }) -> 'list[Any]':
        """Return all documents with a given projection

        Args:
            projection (dict): dict to filter attributes of returned documents by. Defaults to { "id": True, "filename": True, "path": True, "thumbnail": True }

        Returns:
            list (Any): list of found documents
        """
        return self.get_multiple({}, projection)

    def get_all_ids(self) -> 'Union[list[Any], None]':
        """Return all ids in image collection

        Returns:
            list (Any): list of documents found
        """
        if not self.is_db_empty():
            return self.get_all(self.id_projection)
        return None

    def get_all_fullsize(self) -> 'Union[list[Any], None]':
        """Return all fullsize images in image collection

        Returns:
            list (Any): list of documents found
        """
        if not self.is_db_empty():
            return self.get_all(self.fullsize_projection)
        return None
    
    def get_multiple_by_id(self, ids: 'list[int]', projection: dict) -> 'Union[list[Any], None]':
        """Return multiple documents specified by ids

        Args:
            ids (list (int)): ids of images in image collection to be returned
            projection (dict): dict to filter attributes of returned documents by

        Returns:
            list (Any): list of documents found
        """
        if ids != None and len(ids) != 0 and not self.is_db_empty():
            filter = {"id": {"$in" : ids}}
            return self.get_multiple(filter, projection)
        return None

    def are_all_ids_in_database(self, ids: 'list[int]') -> 'Union[Tuple[Literal[False], str], Tuple[Literal[True], None]]':
        """Checks if all given ids are in image collection

        Args:
            ids (list (int)): ids of images in image collection to be assessed

        Returns:
            bool: True if all are in databse, False if one or more are not in database 
            str_or_None: None if bool is True, error message if bool is False
        """
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

    def get_multiple_fullsize_by_id(self, ids: 'list[int]') -> 'Union[list[Any], None]':
        """Return multiple fullsize images specified by ids

        Args:
            ids (list (int)): ids of images in image collection to be returned

        Returns:
            list (Any): list of documents found
        """
        return self.get_multiple_by_id(ids, self.fullsize_projection)

    def get_thumbnail_fs_id(self, picture_id: int) -> 'Union[Any, None]':
        """Returns the GridFS id for a given picture id, indicating which thumbnail to search for

        Args:
            picture_id (int): Id of document to be found in image collection, whose thumbnail shall be returned

        Returns:
            Any: GridFS id of thumbnail
        """
        return self.get_one_by_id(picture_id, { "thumbnail": True })["thumbnail"]

    def get_one_thumbnail_by_id(self, entry_id: int) -> 'Union[Any, None]':
        """Return one thumbnail specified by entry_id

        Args:
            entry_id (int): id of image whose thumbnail shall be returned

        Returns:
            Any: thumbnail returned by GridFS
        """
        id = self.get_thumbnail_fs_id(entry_id)
        return self._gridfs.get(id)
        
    def get_all_thumbnails(self) -> 'Union[list[Any], None]':
        """Return all thumbnails present in GridFS collection

        Returns:
            list (Any): all thumbnails present
        """
        if not self.is_db_empty():
            result = self._gridfs.find({ "metadata" : "thumbnail" })
            if not result is None:
                return [ x for x in result ]    
            return None 
        return None

    def get_multiple_thumbnails_by_id(self, ids: 'list[int]') -> 'Union[list[Any], None]':
        """Return the thumbnails from the GridFS collection specified by ids

        Args:
            ids (list (int)): ids of images in GridFS collection to be returned

        Returns:
            list (Any): list of thumbnails found
        """
        if not self.is_db_empty():
            fs_ids = self.get_multiple_by_id(ids, { "thumbnail": True })
            fs_ids = [ x["thumbnail"] for x in fs_ids ]
            result = self._gridfs.find({ "_id": {"$in" : fs_ids}, "metadata": "thumbnail" })
            if not result is None:
                return [ x for x in result ]

    def get_coordinates(self, id: int) -> 'Union[Tuple[float, float], None]':
        """Return the coordinates of the images specified by id

        Args:
            id (int): id of the image in image collection, whose coordinates shall be returned

        Returns:
            tulple (float, float): tuple of x and y, the coordinates of the image
        """
        result = self.get_one_by_id(id, { "x": True, "y": True})
        if not result is None:
            x = result["x"]
            y = result["y"]
            return (x, y)
        return None

    def get_metadata(self, id: int) -> dict:
        """Return the metadata of an image in the images collection

        Args:
            id (int): id of the image

        Returns:
            dict: metadata of the image specified by id
        """
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
    
    def get_multiple_metadata(self, ids: 'list[int]') -> 'list[dict]':
        """Return the metadata of the images specified by ids

        Args:
            id (list (int)): ids for which the metadata shall be found

        Returns:
            list (dict): list of dicts containing the metadata of the specified images
        """
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

    def get_all_metadata(self) -> 'list[dict]':
        """Return the metadata all images in the image collection

        Returns:
            list (dict): list of dicts containing the metadata of all images
        """
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

    def get_one_filename(self, id: int) -> str:
        """Return the filename of one image specified by id

        Args:
            id (int): id of image to be found

        Returns:
            str: filename of the image
        """
        return self.get_one_by_id(id, { "filename": True })["filename"]

    def ids_to_various(self, ids: 'list[int]', **kwargs: 'dict[str, bool]') -> 'Union[dict[str, list[Any]], None]':
        """Flexible method used to find images specified by id and arguments specified in kwargs

        Args:
            ids (list (int)): ids of images to be found
            kwargs (dict): should contain all columns of the image collection to be returned, specify by <col>=True

        Returns:
            dict (str, list (Any)): dict containing the columns as keys and results as values
        """
        if ids is None:
            return None
        if not isinstance(ids, np.ndarray):
            return None
        if ids.ndim == 1:
            ids = ids.reshape(1, -1)
        values_correct = all(key in self.possible_search_parameters for key in kwargs.keys())
        if not values_correct:
            return None
        query = { key: True for key in kwargs.keys() }
        query["id"] = True
        results = { key: [] for key in query.keys() }
        for row in ids:
            row = row.tolist()
            df = DataFrame(list(self.get_multiple_by_id(row, query)))
            lists = { key: [] for key in query.keys() }
            for idx in row:
                item = df.loc[df["id"] == idx].to_dict()
                for key, val in item.items():
                    lists[key].append(
                        self.type_reg[key](
                            list(
                                val.values()
                            )[0]
                        )
                    )
            for key in query.keys():
                results[key].append(lists[key])
        return results

    def ids_to_filenames(self, ids: 'list[int]') -> 'Union[list[str], None]':
        """Return all filenames specified by ids

        Args:
            list (int): ids whose filenames shall be found

        Returns:
            list (str): list of filenames
        """
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

    def update_labels(self, labels: 'list[int]') -> None:
        """Reassign values to cluster_centers 

        Args:
            labels (list[int]): cluster_centers
        """
        updateOps = [
            UpdateOne({ "id": idx }, { "$set": { "cluster_center": int(item) }}) for idx, item in enumerate(labels)
        ]
        self.col.bulk_write(updateOps)

    def get_one_label(self, id: int) -> Any:
        """Return the label of image specified by id

        Args:
            id (int): id of the image

        Returns:
            Any: cluster center
        """
        return self.get_metadata(id)["cluster_center"]

def get_instance() -> Database:
    """Return the current and preferably only instance of Database. If possible use this function to access the class methods of this class.

    Returns:
        Database: current instance of Database
    """
    return _instance

# Create the current and preferably only instance of Database
_instance = Database()
