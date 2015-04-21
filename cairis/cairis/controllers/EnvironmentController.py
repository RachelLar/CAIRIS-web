import cherrypy
from SessionValidator import validate_proxy
from jsonpickle import encode as json_serialize

__author__ = 'student'


class EnvironmentController(object):
    def all(self, conf=None, constraintsId=-1):
        db_proxy = validate_proxy(cherrypy.session, conf)
        environments = db_proxy.getEnvironments(constraintsId)
        return json_serialize(environments)

    def all_names(self, conf=None):
        db_proxy = validate_proxy(cherrypy.session, conf)
        environment_names = db_proxy.getEnvironmentNames()
        return json_serialize(environment_names)