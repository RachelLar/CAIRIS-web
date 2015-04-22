from CairisHTTPError import CairisHTTPError
from jsonpickle import decode as json_deserialize
from MySQLDatabaseProxy import MySQLDatabaseProxy

__author__ = 'Robin Quetin'


def validate_proxy(session, conf):
    if conf is None:
        db_proxy = session.get('dbProxy', None)
        if db_proxy is None:
            CairisHTTPError(msg='The method is not callable without setting up a database connection.')
        elif isinstance(db_proxy, MySQLDatabaseProxy):
            return db_proxy
        else:
            CairisHTTPError(msg='The database connection was not properly set up. Please try to reset the connection.')
    else:
        if not isinstance(conf, dict):
            try:
                conf = json_deserialize(conf)
            except Exception, e:
                CairisHTTPError(msg=str(e.message))

        db_proxy = MySQLDatabaseProxy(conf['host'], conf['port'], conf['user'], conf['passwd'], conf['db'])
        if db_proxy is not None:
            return db_proxy
        else:
            CairisHTTPError(msg='Failed to configure the database connection')

def validate_fonts(session, conf):
    if conf is None:
        fontName = session.get('fontName', None)
        fontSize = session.get('fontSize', None)
        apFontName = session.get('apFontSize', None)

        if fontName is None or fontSize is None or apFontName is None:
            CairisHTTPError(msg='The method is not callable without setting up the project settings.')
        elif isinstance(fontName, str) and isinstance(fontSize, str) and isinstance(apFontName, str):
            return fontName, fontSize, apFontName
        else:
            CairisHTTPError(msg='The database connection was not properly set up. Please try to reset the connection.')
    else:
        if all(k in conf for k in ('fontName', 'fontSize', 'apFontName')):
            return conf['fontName'], conf['fontSize'], conf['apFontName']
        else:
            CairisHTTPError(msg='Failed to configure the project settings')