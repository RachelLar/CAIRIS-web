from flask import request, make_response
from Borg import Borg
from tools.JsonConverter import json_serialize
from werkzeug.exceptions import HTTPException

__author__ = 'Robin Quetin'

class CairisHTTPError(HTTPException):
    def __init__(self, status_code, message, status='Invalid input'):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.status = status
        self.valid_methods = ['GET', 'POST', 'PUT', 'DELETE']
        self.__setattr__('code', status_code)
        self.__setattr__('data', {'status': status_code, 'message': message})

        accept_header = request.headers.get('Accept', 'application/json')
        if accept_header.find('text/html') > -1:
            self.response = make_response(self.handle_exception_html(), self.status_code)
        else:
            self.response = make_response(self.handle_exception_json(), self.status_code)

    def handle_exception_html(self):
        b = Borg()
        return b.template_generator.serve_result('common.error', msg=self.message, code=self.status_code, title=self.status)

    def handle_exception_json(self):
        return json_serialize({'message': self.message, 'code': self.status_code, 'status': self.status})