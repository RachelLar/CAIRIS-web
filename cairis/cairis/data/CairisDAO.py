import httplib

from Borg import Borg
from CairisHTTPError import CairisHTTPError
from MySQLDatabaseProxy import MySQLDatabaseProxy


__author__ = 'Robin Quetin'

class CairisDAO(object):
    def __init__(self, session_id):
        self.db_proxy = self.get_dbproxy(session_id)

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