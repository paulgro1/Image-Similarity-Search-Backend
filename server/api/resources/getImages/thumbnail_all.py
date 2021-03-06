"""Module contains Resource to get all thmbnails"""
from flask_restful import Resource, abort
from flask import send_file
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED

import api.db as db


class AllThumbnails(Resource):
    """Resource returns thumbnails on get request"""

    def get(self):
        """HTTP GET request used to return all thumbnails as a zip directory

        Returns:
            Any: data for response
        """
        all_images = db.get_instance().get_all_thumbnails()
        if all_images is None:
            abort(404, message="No Pictures found")
        # See https://stackoverflow.com/questions/2463770/python-in-memory-zip-library
        buffer = BytesIO()
        with ZipFile(buffer, "a", ZIP_DEFLATED, False) as zip_file:
            for item in all_images:
                the_id = item.id
                zip_file.writestr(f"{the_id}_{item.filename}", item.read())
        buffer.seek(0)
        return send_file(buffer, attachment_filename="thumbnails.zip", as_attachment=True)
