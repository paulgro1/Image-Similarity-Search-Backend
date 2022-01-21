"""Module contains Resource to get multiple thumbnails"""
from flask_restful import Resource, abort
from flask import request, send_file
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED

import api_package.db as db
from api_package.helper import abort_if_pictures_dont_exist


class MultipleThumbnails(Resource):
    """Resource returns multiple thumbnails on post request"""
    
    def post(self):
        """HTTP POST request used to return multiple thumbnails specified in json body array picture_ids

        Returns:
            Any: data for response
        """
        if not "picture_ids" in request.json:
            abort(404, message="No picture ids present in json body")
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
