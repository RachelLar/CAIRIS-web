import httplib
import imghdr
import os
import uuid

from werkzeug.datastructures import FileStorage

from Borg import Borg
from CairisHTTPError import CairisHTTPError
from data.CairisDAO import CairisDAO

__author__ = 'Robin Quetin'


class UploadDAO(CairisDAO):
    accepted_image_types = ['jpg', 'jpeg', 'png', 'bmp', 'gif']

    def __init__(self, session_id):
        CairisDAO.__init__(self, session_id)
        b = Borg()
        self.image_dir = os.path.join(b.uploadDir, 'images')

    def upload_image(self, file):
        """
        :type file: FileStorage
        """
        extension = os.path.splitext(file.filename)[1]
        f_name = str(uuid.uuid4()) + extension
        f_path = os.path.join(self.image_dir, f_name)

        try:
            file.save(f_path)
        except IOError:
            raise CairisHTTPError(
                status_code=httplib.CONFLICT,
                status='Unable to save image',
                message='Please check if the static web directory exists ' +
                        'and if the application has permission to write in the directory',
            )

        if not os.path.exists(f_path):
            raise CairisHTTPError(
                status_code=httplib.CONFLICT,
                status='Image not found',
                message='The image could not be saved on the server. \
Please check the server configuration to fix this problem.'
            )
        img_format = imghdr.what(f_path)
        if not img_format or img_format not in self.accepted_image_types:
            os.remove(f_name)
            raise CairisHTTPError(
                status_code=httplib.CONFLICT,
                status='Unsupported file type',
                message='The provided image file is not supported by CAIRIS'
            )
        return f_name