import logging
from urllib import quote
from StringIO import StringIO

import jsonpickle

from tests.CairisTests import CairisTests

__author__ = 'Robin Quetin'


class CImportTests(CairisTests):
    xmlfile = '/home/robin/Documents/CAIRIS-web/cairis/examples/completeExample.xml'
    logger = logging.getLogger(__name__)

    def test_cimport_data_post(self):
        method = 'test_cimport_text_post'
        url = '/api/import/text'
        fs_xmlfile = open(self.xmlfile, 'rb')
        file_contents = fs_xmlfile.read()
        self.logger.info('[%s] URL: %s', method, url)
        self.logger.debug('[%s] XML file:\n%s', method, file_contents)

        urlenc_file_contents = quote(file_contents)
        json_dict = {
            'session_id': 'test',
            'object': {
                'urlenc_file_contents': urlenc_file_contents,
                'type': 'all'
            }
        }
        json_body = jsonpickle.encode(json_dict)
        rv = self.app.post(url, data=json_body, content_type='application/json')
        self.assertIsNotNone(rv.data, 'No response')
        json_dict = jsonpickle.decode(rv.data)
        self.assertIsInstance(json_dict, dict, 'The response is not a valid JSON dictionary')
        assert isinstance(json_dict, dict)
        message = json_dict.get('message')
        self.assertIsNotNone(message, 'Response does not contain a message')
        self.logger.info('[%s] Message: %s', method, message)
        self.assertGreater(message.find('Imported'), -1, 'Nothing imported')

    def test_cimport_file_post(self):
        method = 'test_cimport_file_post'
        type = 'all'
        url = '/api/import/file/type/%s?session_id=test' % quote(type)
        fs_xmlfile = open(self.xmlfile, 'rb')
        file_contents = fs_xmlfile.read()
        self.logger.info('[%s] URL: %s', method, url)
        self.logger.debug('[%s] XML file:\n%s', method, file_contents)

        data = {
            'file': (StringIO(file_contents), 'import.xml'),
            'session_id': 'test'
        }
        rv = self.app.post(url, data=data, content_type='multipart/form-data')
        self.assertIsNotNone(rv.data, 'No response')
        json_dict = jsonpickle.decode(rv.data)
        self.assertIsInstance(json_dict, dict, 'The response is not a valid JSON dictionary')
        assert isinstance(json_dict, dict)
        message = json_dict.get('message')
        self.assertIsNotNone(message, 'Response does not contain a message')
        self.logger.info('[%s] Message: %s', method, message)
        self.assertGreater(message.find('Imported'), -1, 'Nothing imported')