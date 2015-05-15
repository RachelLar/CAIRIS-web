import logging
import jsonpickle
from tests.CairisTests import CairisTests
from tools.JsonConverter import json_serialize


__author__ = 'Robin Quetin'


class UserTests(CairisTests):
    logger = logging.getLogger('UserTests')
    data = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'cairis',
        'passwd': 'cairis123',
        'db': 'cairis',
        'jsonPrettyPrint': 'on'
    }

    def test_user_config_form_post(self):
        rv = self.app.post('/user/config.html', data=self.data, headers={'accept': 'text/html'})
        self.assertIsNotNone(rv.data, 'No response')
        self.logger.info('Data: %s', rv.data)
        check = rv.data.find('session_id')
        self.assertGreater(check, -1, 'No session ID was returned')

    def test_user_config_json_post(self):
        data_str = jsonpickle.encode(self.data)
        rv = self.app.post('/api/user/config', content_type='application/json', data=data_str)
        self.assertIsNotNone(rv.data, 'No response')
        self.logger.info('Data: %s', rv.data)
        resp_dict = jsonpickle.decode(rv.data)
        self.assertIsNotNone(resp_dict, 'Unable to deserialize response')
        self.assertIsNotNone(resp_dict.get('session_id', None), 'No session ID defined')