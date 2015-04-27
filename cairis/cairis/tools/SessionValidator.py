from flask.ext.restful import abort
from ARM import DatabaseProxyException
from Borg import Borg
from MySQLDatabaseProxy import MySQLDatabaseProxy

__author__ = 'Robin Quetin'


def check_required_keys(json_dict, required):
    if not all(reqKey in json_dict for reqKey in required):
        abort(405, 'Some required parameters are missing.')

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
            abort(message='The method is not callable without setting up a database connection.')
        elif isinstance(db_proxy, MySQLDatabaseProxy):
            return db_proxy
        else:
            abort(400, message='The database connection was not properly set up. Please try to reset the connection.')
    else:
        abort(400, message='The method is not callable without setting up a database connection.')

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
            abort(400, message='The method is not callable without setting up the project settings.')
        elif isinstance(fontName, str) and isinstance(fontSize, str) and isinstance(apFontName, str):
            return fontName, fontSize, apFontName
        else:
            abort(400, message='The database connection was not properly set up. Please try to reset the connection.')
    else:
        abort(400, message='The method is not callable without setting up the project settings.')