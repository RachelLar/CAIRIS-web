import httplib
import imghdr
import os
import uuid
from Borg import Borg
from CairisHTTPError import CairisHTTPError
from data.CairisDAO import CairisDAO
from tools.JsonConverter import json_serialize
from werkzeug.datastructures import FileStorage

__author__ = 'Robin Quetin'


accepted_image_types = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
class UploadDAO(CairisDAO):
    def __init__(self, session_id):
        CairisDAO.__init__(self, session_id)
        b = Borg()
        self.image_dir = os.path.join(b.staticDir, 'images')

    def upload_image(self, file):
        """
        :type file: FileStorage
        """

        extension = os.path.splitext(file.filename)[1]
        f_name = str(uuid.uuid4()) + extension
        f_path = os.path.join(self.image_dir, f_name)
        file.save(f_path)

        if not os.path.exists(f_path):
            raise CairisHTTPError(
                status_code=httplib.CONFLICT,
                status='Image not found',
                message='The image could not be saved on the server. Please check the server configuration to fix this problem.'
            )
        img_format = imghdr.what(f_path)
        if not img_format:
            os.remove(f_name)
            raise CairisHTTPError(
                status_code=httplib.CONFLICT,
                status='Unsupported file type',
                message='The provided image file is not supported by CAIRIS'
            )
        return f_name