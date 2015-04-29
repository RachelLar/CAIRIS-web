from flask.ext.restful import abort
from ARM import DatabaseProxyException
from Borg import Borg
from CairisHTTPError import CairisHTTPError
from MySQLDatabaseProxy import MySQLDatabaseProxy

__author__ = 'Robin Quetin'


def check_required_keys(json_dict, required):
    if not all(reqKey in json_dict for reqKey in required):
        raise CairisHTTPError(405, 'Some required parameters are missing.')

def validate_proxy(session, id, conf=None):
    """
    Validates that the DB proxy object is properly set up
    :param session: The session object of the request
    :param id: The session ID provided by the user
    :param conf: A dictionary containing configuration settings for direct authenrication
    :return: The MySQLDatabaseProxy object associated to the session
    :rtype : MySQLDatabaseProxy
    :raise CairisHTTPError: Raises a CairisHTTPError when the database could not be properly set up
    """

    if session is not None:
        session_id = session.get('session_id', -1)
    else:
        session_id = -1

    if conf is not None:
        if isinstance(conf, dict):
            try:
                db_proxy = MySQLDatabaseProxy(host=conf['host'], port=conf['port'], user=conf['user'], passwd=conf['passwd'], db=conf['db'])
                if db_proxy is not None:
                    return db_proxy
                else:
                    raise CairisHTTPError(400, message='The database connection could not be created.')
            except DatabaseProxyException:
                raise CairisHTTPError(405, message='The provided settings are invalid and cannot be used to create a database connection')

    if not (session_id == -1 and id is None):
        if id is None:
            id = session_id
        b = Borg()
        db_proxy = b.get_dbproxy(id)

        if db_proxy is None:
            raise CairisHTTPError(400, message='The database connection could not be created.')
        elif isinstance(db_proxy, MySQLDatabaseProxy):
            return db_proxy
        else:
            raise CairisHTTPError(400, message='The database connection was not properly set up. Please try to reset the connection.')
    else:
        raise CairisHTTPError(405, message='The session is neither started or no session ID is provided with the request.')

def validate_fonts(session, id):
    """
    Validates that the fonts to output the SVG models are properly set up
    :param session: The session object of the request
    :param id: The session ID provided by the user
    :return: The font name, font size and AP font name
    :rtype : str,str,str
    :raise CairisHTTPError: Raises a CairisHTTPError when the database could not be properly set up
    """

    if session is not None:
        session_id = session.get('session_id', -1)
    else:
        session_id = -1

    if not (session_id == -1 and id is None):
        if id is None:
            id = session_id

        b = Borg()
        settings = b.get_settings(id)
        fontName = settings.get('fontName', None)
        fontSize = settings.get('fontSize', None)
        apFontName = settings.get('apFontSize', None)

        if fontName is None or fontSize is None or apFontName is None:
            raise CairisHTTPError(400, message='The method is not callable without setting up the project settings.')
        elif isinstance(fontName, str) and isinstance(fontSize, str) and isinstance(apFontName, str):
            return fontName, fontSize, apFontName
        else:
            raise CairisHTTPError(400, message='The database connection was not properly set up. Please try to reset the connection.')
    else:
        raise CairisHTTPError(400, message='The method is not callable without setting up the project settings.')