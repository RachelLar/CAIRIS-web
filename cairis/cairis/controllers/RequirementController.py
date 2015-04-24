import cherrypy

from CairisHTTPError import CairisHTTPError
from tools.SessionValidator import validate_proxy
from tools.JsonConverter import json_serialize, json_deserialize


__author__ = 'Robin Quetin'


# noinspection PyMethodMayBeStatic
class RequirementController(object):
    def all(self, constraintId='', isAsset=1, session_id=None):
        accept_header = cherrypy.request.headers.get('Accept', None)
        if accept_header.find('application/json')+accept_header.find('text/plain') > -2:
            cherrypy.response.headers['Content-Type'] = accept_header
        elif accept_header.find('*/*') > -1:
            cherrypy.response.headers['Content-Type'] = 'application/json'
        else:
            CairisHTTPError(msg='Not Acceptable', code=406, status='Not Acceptable')

        db_proxy = validate_proxy(cherrypy.session, session_id)
        reqs = db_proxy.getRequirements(constraintId, isAsset)
        return json_serialize(reqs, session_id=session_id)

    def get_requirement(self, id, session_id=None):
        accept_header = cherrypy.request.headers.get('Accept', None)
        if accept_header.find('application/json')+accept_header.find('text/plain') > -2:
            cherrypy.response.headers['Content-Type'] = accept_header
        elif accept_header.find('*/*') > -1:
            cherrypy.response.headers['Content-Type'] = 'application/json'
        else:
            CairisHTTPError(msg='Not Acceptable', code=406, status='Not Acceptable')

        db_proxy = validate_proxy(cherrypy.session, session_id)
        req = db_proxy.getRequirement(id)
        return json_serialize(req, session_id=session_id)

    def update_requirement(self, requirement, session_id=None):
        db_proxy = validate_proxy(cherrypy.session, session_id)
        reqObj = json_deserialize(requirement, 'requirement')
        db_proxy.updateRequirement(reqObj)
        msg = 'Requirement successfully updated'
        code = 200
        status = 'OK'
        return json_serialize({'message': msg, 'code': code, 'status': status}, session_id=session_id)
