import cherrypy

from CairisHTTPError import CairisHTTPError
from tools.SessionValidator import validate_proxy
from tools.JsonConverter import json_serialize, json_deserialize


__author__ = 'Robin Quetin'


# noinspection PyMethodMayBeStatic
class RequirementController(object):
    def all(self, is_asset=1, ordered=1, session_id=None):
        db_proxy = validate_proxy(cherrypy.session, session_id)
        if ordered == 1:
            reqs = db_proxy.getOrderedRequirements('', is_asset==1)
        else:
            reqs = db_proxy.getRequirements('', is_asset)
        return json_serialize(reqs, session_id=session_id)

    def get_filtered_requirements(self, filter, is_asset=1, ordered=1, session_id=None):
        db_proxy = validate_proxy(cherrypy.session, session_id)
        if ordered == 1:
            reqs = db_proxy.getOrderedRequirements(filter, is_asset==1)
        else:
            reqs = db_proxy.getRequirements(filter, is_asset)
        return json_serialize(reqs, session_id=session_id)

    def get_requirement_by_id(self, id, session_id=None):
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
