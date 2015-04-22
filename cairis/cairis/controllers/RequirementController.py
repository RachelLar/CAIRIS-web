import cherrypy
import json
import JsonToObjectConverter
from jsonpickle import encode as json_serialize
from jsonpickle import decode as json_deserialize
from CairisHTTPError import CairisHTTPError
from SessionValidator import validate_proxy

__author__ = 'Robin Quetin'


# noinspection PyMethodMayBeStatic
class RequirementController(object):
    def all(self, constraintId='', isAsset=1, conf=None):
        accept_header = cherrypy.request.headers.get('Accept', None)
        if accept_header.find('application/json')+accept_header.find('text/plain') > -2:
            cherrypy.response.headers['Content-Type'] = accept_header
        elif accept_header.find('*/*') > -1:
            cherrypy.response.headers['Content-Type'] = 'application/json'
        else:
            CairisHTTPError(msg='Not Acceptable', code=406, status='Not Acceptable')

        db_proxy = validate_proxy(cherrypy.session, conf)
        reqs = db_proxy.getRequirements(constraintId, isAsset)
        return json.dumps(json.loads(json_serialize(reqs)), indent=4)
        return json_serialize(reqs)

    def get_requirement(self, id, conf=None):
        accept_header = cherrypy.request.headers.get('Accept', None)
        if accept_header.find('application/json')+accept_header.find('text/plain') > -2:
            cherrypy.response.headers['Content-Type'] = accept_header
        elif accept_header.find('*/*') > -1:
            cherrypy.response.headers['Content-Type'] = 'application/json'
        else:
            CairisHTTPError(msg='Not Acceptable', code=406, status='Not Acceptable')

        db_proxy = validate_proxy(cherrypy.session, conf)
        req = db_proxy.getRequirement(id)
        return json.dumps(json.loads(json_serialize(req)), indent=4)
        return json_serialize(req)

    def update_requirement(self, requirement, conf=None):
        db_proxy = validate_proxy(cherrypy.session, conf)
        reqDict = json_deserialize(requirement)
        reqObj = JsonToObjectConverter.convert(reqDict, 'requirement')
        #db_proxy.updateRequirement(reqObj)
