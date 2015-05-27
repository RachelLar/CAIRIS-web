import logging
import os
import urllib
from StringIO import StringIO
from tests.CairisTests import CairisTests

__author__ = 'Robin Quetin'


class UploadTests(CairisTests):
    logger = logging.getLogger(__name__)

    def test_image_upload(self):
        method = 'test_image_upload'
        name, request = urllib.urlretrieve('http://high-resolution-photos.com/stock_photos/royalty_free_3.jpg')
        if name and os.path.exists(name):
            fs_image = open(name, 'rb')
            image_bytes = fs_image.read()
            rv = self.app.post('/api/upload/image?session_id=test', data={
                'file': (StringIO(image_bytes), name),
            })
            self.logger.info('[%s] Response data: %s', method, rv.data)

    def test_big_image_upload(self):
        method = 'test_big_image_upload'
        name, request = urllib.urlretrieve('http://upload.wikimedia.org/wikipedia/commons/d/d4/Nature_landscape_ukraine_poltava_(8093169218).jpg')
        if name and os.path.exists(name):
            fs_image = open(name, 'rb')
            image_bytes = fs_image.read()
            rv = self.app.post('/api/upload/image?session_id=test', data={
                'file': (StringIO(image_bytes), name),
            })
            self.logger.info('[%s] Response data: %s', method, rv.data)