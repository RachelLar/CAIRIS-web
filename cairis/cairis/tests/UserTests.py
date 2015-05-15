import logging
from urllib import quote

from tests.CairisTests import CairisTests


__author__ = 'Robin Quetin'


class UserTests(CairisTests):

    logger = logging.getLogger('UserTests')

    def test_user_config_form_post(self):
        data = {
            'host': '127.0.0.1',
            'port': '3306',
            'user': 'cairis',
            'passwd': 'cairis123',
            'db': 'cairis',
            'jsonPrettyPrint': 'on'
        }

        data_str = ''
        for form_key, form_value in data.items():
            data_str += '%s=%s&' % (quote(form_key), quote(form_value))

        rv = self.app.post('/user/config.html', data=data_str[:-1], content_type='application/www-x-form-urlencoded')
        self.assertIsNotNone(rv.data, 'No response')
        self.logger.info('Data: %s', rv.data)
        check = rv.data.find('session_id')
        self.assertGreater(check, -1, 'No session ID was returned')