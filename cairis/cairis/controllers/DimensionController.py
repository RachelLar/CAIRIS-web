import cherrypy
from tools.JsonConverter import json_serialize
from tools.SessionValidator import validate_proxy

__author__ = 'TChosenOne'

class DimensionController(object):
    def get_dimensions(self, table, id=-1, session_id=None):
        db_proxy = validate_proxy(cherrypy.session, session_id)
        dimensions = db_proxy.getDimensions(table, id)
        return json_serialize(dimensions, session_id=session_id)

    def get_dimension_names(self, table, environment='', session_id=None):
        db_proxy = validate_proxy(cherrypy.session, session_id)
        dimension_names = db_proxy.getDimensionNames(table, environment)
        return json_serialize(dimension_names, session_id=session_id)