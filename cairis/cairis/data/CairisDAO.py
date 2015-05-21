import httplib
import logging

from Borg import Borg
from CairisHTTPError import CairisHTTPError, MalformedJSONHTTPError
from MySQLDatabaseProxy import MySQLDatabaseProxy
from ValueType import ValueType
from tools.JsonConverter import json_serialize, json_deserialize
from tools.ModelDefinitions import ValueTypeModel
from tools.SessionValidator import check_required_keys

__author__ = 'Robin Quetin'

class CairisDAO(object):
    def __init__(self, session_id):
        b = Borg()
        self.db_proxy = self.get_dbproxy(session_id)
        self.logger = logging.getLogger('cairisd')
        self.logger.setLevel(b.logLevel)

    def from_json(self, request):
        raise NotImplementedError('from_json is not yet implemented by subclass')

    def type_from_json(self, request):
        json = request.get_json(silent=True)
        if json is False or json is None:
            raise MalformedJSONHTTPError(data=request.get_data())

        json_dict = json['object']
        check_required_keys(json_dict, ValueTypeModel.required)
        json_dict['__python_obj__'] = ValueType.__module__+'.'+ValueType.__name__

        value_type = json_serialize(json_dict)
        value_type = json_deserialize(value_type)
        if not isinstance(value_type, ValueType):
            raise MalformedJSONHTTPError(data=request.get_data())
        else:
            return value_type

    def simplify(self, obj):
        raise NotImplementedError('from_json is not yet implemented by subclass')

    def get_dbproxy(self, session_id):
        """
        Searches the MySQLDatabaseProxy instance associated with the session ID.
        :param session_id: The session ID
        :type session_id: str
        :return The MySQLDatabaseProxy instance associated with the session ID
        :rtype MySQLDatabaseProxy
        """
        if session_id != -1:
            b = Borg()
            db_proxy = b.get_dbproxy(session_id)

            if db_proxy is None:
                raise CairisHTTPError(
                    status_code=httplib.CONFLICT,
                    message='The database connection could not be created.'
                )
            elif isinstance(db_proxy, MySQLDatabaseProxy):
                db_proxy.reconnect(session_id=session_id)
                return db_proxy
            else:
                raise CairisHTTPError(
                    status_code=httplib.CONFLICT,
                    message='The database connection was not properly set up. Please try to reset the connection.'
                )
        else:
            raise CairisHTTPError(
                status_code=httplib.BAD_REQUEST,
                message='The session is neither started or no session ID is provided with the request.'
            )