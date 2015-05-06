import httplib

from flask import request, make_response
from werkzeug.exceptions import HTTPException

from ARM import ARMException, DatabaseProxyException
from Borg import Borg
from tools.JsonConverter import json_serialize


__author__ = 'Robin Quetin'


def handle_exception(ex):
    """
    Handles a undefined exception in the most correct way possible.
    :param ex: The caught exception
    :type ex: Exception
    """
    if isinstance(ex, ARMException):
        raise ARMHTTPError(ex)
    elif isinstance(ex, DatabaseProxyException):
        raise ARMHTTPError(ex)
    elif isinstance(ex, LookupError):
        raise MissingParameterHTTPError(exception=ex)
    elif isinstance(ex, TypeError):
        if ex.message.find('decode() argument 1 must be string, not None') > -1:
            raise MalformedJSONHTTPError()

    raise CairisHTTPError(
        status_code=httplib.INTERNAL_SERVER_ERROR,
        message=str(ex.message),
        status='Undefined error'
    )

class CairisHTTPError(HTTPException):
    def __init__(self, status_code, message, status='Invalid input'):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.status = status
        self.valid_methods = ['GET', 'POST', 'PUT', 'DELETE']
        self.__setattr__('code', status_code)

        accept_header = request.headers.get('Accept', 'application/json')
        if accept_header.find('text/html') > -1:
            self.response = make_response(self.handle_exception_html(), self.status_code)
        else:
            self.response = make_response(self.handle_exception_json(), self.status_code)

    def handle_exception_html(self):
        b = Borg()
        message = b.template_generator.prepare_message(self.message)
        self.__setattr__('data', message)
        return b.template_generator.serve_result('common.error', msg=message, code=self.status_code, title=self.status)

    def handle_exception_json(self):
        self.__setattr__('data', {'message': self.message, 'code': self.status_code, 'status': self.status})
        return json_serialize({'message': self.message, 'code': self.status_code, 'status': self.status})

class ARMHTTPError(CairisHTTPError):
    def __init__(self, exception):
        """

        :type exception: ARMException
        """
        CairisHTTPError.__init__(self,
            status_code=httplib.CONFLICT,
            message=exception.value,
            status='Database conflict'
        )

class MalformedJSONHTTPError(CairisHTTPError):
    def __init__(self):
        CairisHTTPError.__init__(self,
            status_code=httplib.BAD_REQUEST,
            message='The request body could not be converted to a JSON object.' +
                    '''Check if the request content type is 'application/json' ''' +
                    'and that the JSON string is well-formed',
            status='Unreadable JSON data'
        )

class MissingParameterHTTPError(CairisHTTPError):
    def __init__(self, exception=None, param_names=None):
        """
        :param exception: The LookupError instance that was raised
        :type exception: LookupError
        :param param_names: A collection of parameter names that are required
        :type param_names: collections.Iterable
        """
        if exception is not None:
            msg = str(exception)
        else:
            msg = 'One or more parameters are missing or invalid. '+\
                  'Please check your request if it contains all the required parameters.'

        if param_names is not None:
            msg += '\nRequired parameters:'
            for param_name in param_names:
                msg += '\n* {}'.format(param_name)

        CairisHTTPError.__init__(
            self,
            status_code=httplib.BAD_REQUEST,
            message=msg,
            status='One or more parameters are missing'
        )