from flask_restful import Resource, abort
from flask import request, send_file
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from api_package.helper import abort_if_pictures_dont_exist
import api_package.db as db

class MultipleThumbnails(Resource):
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
        print(f"Getting thumbnails for ids { picture_ids } ")
        images = db.get_instance().get_multiple_thumbnails_by_id(picture_ids)
        if images is None:
            abort(404, message=f"Picture(s) {picture_ids} not found")
        # See https://stackoverflow.com/questions/2463770/python-in-memory-zip-library
        buffer = BytesIO()
        with ZipFile(buffer, "a", ZIP_DEFLATED, False) as zip_file:
            for item in images:
                the_id = item.id
                zip_file.writestr(f"{the_id}_{item.filename}", item.read())
        buffer.seek(0)
        return send_file(buffer, attachment_filename="thumbnails.zip", as_attachment=True)