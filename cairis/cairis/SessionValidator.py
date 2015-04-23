from ARM import DatabaseProxyException
from Borg import Borg
from CairisHTTPError import CairisHTTPError
from jsonpickle import decode as json_deserialize
from MySQLDatabaseProxy import MySQLDatabaseProxy

__author__ = 'Robin Quetin'


def validate_proxy(session, id, conf=None):
    if session is not None:
        session_id = session.get('session_id', -1)
    else:
        session_id = -1

    if conf is not None:
        if isinstance(conf, dict):
            try:
                db_proxy = MySQLDatabaseProxy(host=conf['host'], port=conf['port'], user=conf['user'], passwd=conf['passwd'], db=conf['db'])
                return db_proxy
            except DatabaseProxyException:
                return None

    if not (session_id == -1 and id is None):
        if id is None:
            id = session_id
        b = Borg()
        db_proxy = b.get_dbproxy(id)

        if db_proxy is None:
            CairisHTTPError(msg='The method is not callable without setting up a database connection.')
        elif isinstance(db_proxy, MySQLDatabaseProxy):
            return db_proxy
        else:
            CairisHTTPError(msg='The database connection was not properly set up. Please try to reset the connection.')
    else:
        CairisHTTPError(msg='The method is not callable without setting up a database connection.')

def validate_fonts(session, id):
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
            CairisHTTPError(msg='The method is not callable without setting up the project settings.')
        elif isinstance(fontName, str) and isinstance(fontSize, str) and isinstance(apFontName, str):
            return fontName, fontSize, apFontName
        else:
            CairisHTTPError(msg='The database connection was not properly set up. Please try to reset the connection.')
    else:
        CairisHTTPError(msg='The method is not callable without setting up the project settings.')