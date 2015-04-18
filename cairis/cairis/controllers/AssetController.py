import cherrypy
from cherrypy import expose, popargs
from json import dumps as json_serialize
from MySQLDatabaseProxy import MySQLDatabaseProxy

__author__ = 'Robin Quetin'

@popargs('name')
class AssetController(object):
    def all(self):
        '''db_proxy = MySQLDatabaseProxy('127.0.0.1', 3306, 'cairis', 'cairis123', 'cairis')
        cherrypy.session['dbProxy'] = db_proxy'''
        db_proxy = cherrypy.session.get('dbProxy', None)
        if db_proxy is None:
            return 'The method is not callable without setting up a database connection.'
        elif isinstance(db_proxy, MySQLDatabaseProxy):
            assets = db_proxy.getDimensionNames('asset')
            return json_serialize(assets)
        else:
            return "Error!"

    def get_asset(self, name=None):
        if name is not None:
            return 'Name: '+name
        return 'Name not set!'
