from flask import request, session, make_response
from flask.ext.restful import Resource
from flask_restful_swagger import swagger
from tools.JsonConverter import json_serialize
from tools.SessionValidator import validate_proxy
from Role import Role

__author__ = 'Robin Quetin'


class RolesAPI(Resource):
    #region Swagger Doc
    #endregion
    def get(self):
        session_id = request.args.get('session_id', None)
        db_proxy = validate_proxy(session, session_id)
        constraint_id = request.args.get('constraint_id', -1)
        roles = db_proxy.getRoles(constraint_id)

        for key in roles:
            role = roles[key]
            role.theEnvironmentDictionary = {}
            roles[key] = role

        resp = make_response(json_serialize(roles, session_id=session_id))
        resp.headers['Content-Type'] = "application/json"
        return resp