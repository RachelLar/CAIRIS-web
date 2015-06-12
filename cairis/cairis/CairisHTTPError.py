import httplib
import logging

from flask import make_response
from werkzeug.exceptions import HTTPException

from ARM import ARMException, DatabaseProxyException
from tools.JsonConverter import json_serialize

__author__ = 'Robin Quetin'

logger = logging.getLogger('cairisd')


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
        resp_dict = {'code': status_code, 'status': status, 'message': message}
        self.__setattr__('code', status_code)
        self.__setattr__('data', resp_dict)

        logger.error('[{0}] {1}: {2}'.format(status_code, status, message))
        self.__setattr__('data', {'message': self.message, 'code': self.status_code, 'status': self.status})
        json_message = json_serialize({'message': self.message, 'code': self.status_code, 'status': self.status})
        self.response = make_response(json_message, self.status_code)


class ARMHTTPError(CairisHTTPError):
    status_code=httplib.CONFLICT
    status='Database conflict'

    def __init__(self, exception):
        """

        :type exception: ARMException
        """
        real_exception = exception
        if isinstance(real_exception.value, DatabaseProxyException):
            real_exception = real_exception.value
        CairisHTTPError.__init__(self,
            status_code=httplib.CONFLICT,
            message=str(real_exception.value),
            status='Database conflict'
        )

class MalformedJSONHTTPError(CairisHTTPError):
    status='Unreadable JSON data'
    status_code=httplib.BAD_REQUEST,

    def __init__(self, data=None):
        if data is not None:
            logger.debug('Data: %s', data)

        CairisHTTPError.__init__(self,
            status_code=httplib.BAD_REQUEST,
            message='The request body could not be converted to a JSON object.' +
                    '''Check if the request content type is 'application/json' ''' +
                    'and that the JSON string is well-formed.',
            status='Unreadable JSON data'
        )

class MissingParameterHTTPError(CairisHTTPError):
    status_code = httplib.BAD_REQUEST
    status = 'One or more parameters are missing'

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
            status_code=self.status_code,
            message=msg,
            status=self.status_code
        )

class ObjectNotFoundHTTPError(CairisHTTPError):
    status_code=httplib.NOT_FOUND
    status='Object not found'

    def __init__(self, obj):
        CairisHTTPError.__init__(
            self,
            status_code=httplib.NOT_FOUND,
            message='{} could not be found in the database'.format(obj),
            status='Object not found'
        )

class OverwriteNotAllowedHTTPError(CairisHTTPError):
    status_code=httplib.CONFLICT
    status='Object already exists'

    def __init__(self, obj_name):
        CairisHTTPError.__init__(
            self,
            status_code=self.status_code,
            message='{} already exists and cannot be overwritten'.format(obj_name),
            status=self.status
        )

class SilentHTTPError(BaseException):
    def __init__(self, message):
        BaseException.__init__(self)
        logger.warning(message)