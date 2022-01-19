from flask_restful import Resource, abort
import api_package.db as db
from flask import request, send_file
from api_package.helper import abort_if_pictures_dont_exist
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from PIL import Image
from os import path

class MultipleFullsize(Resource):
    """
    TODO Docs
    """
    def post(self):
        """
        HTTP GET method, returns multiple thumbnails from database

        TODO return, docs
        """
        picture_ids = request.json["picture_ids"]
        abort_if_pictures_dont_exist(picture_ids, db.get_instance())
        print(f"Getting fullsize for ids { picture_ids } ")
        images = db.get_instance().get_multiple_fullsize_by_id(picture_ids)
        if images is None:
            abort(404, message=f"Picture(s) {picture_ids} not found")
        # See https://stackoverflow.com/questions/2463770/python-in-memory-zip-library
        buffer = BytesIO()
        with ZipFile(buffer, "a", ZIP_DEFLATED, False) as zip_file:
            for item in images:
                with Image.open(item["path"]) as img:
                    filename = path.split(item["path"])[-1]
                    with BytesIO() as output:
                        img.save(output, format=img.format)
                        the_id = item["id"]
                        zip_file.writestr(f"{the_id}_{filename}", output.getvalue())
        buffer.seek(0)
        return send_file(buffer, attachment_filename="fullsize.zip", as_attachment=True)