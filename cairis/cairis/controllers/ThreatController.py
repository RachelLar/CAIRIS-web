import httplib

from flask import request, session, make_response
from flask.ext.restful import Resource
from flask_restful_swagger import swagger

from data.ThreatDAO import ThreatDAO
from tools.JsonConverter import json_serialize
from tools.MessageDefinitions import ThreatMessage
from tools.ModelDefinitions import ThreatModel
from tools.SessionValidator import get_session_id


__author__ = 'Robin Quetin'


class ThreatAPI(Resource):
    #region Swagger Doc
    @swagger.operation(
        notes='Get all threats',
        nickname='threats-get',
        responseClass=ThreatModel.__name__,
        responseContainer='List',
        parameters=[
            {
                "name": "ordered",
                "description": "Defines if the list has to be order",
                "default": 1,
                "required": False,
                "allowMultiple": False,
                "dataType": int.__name__,
                "paramType": "query"
            },
            {
                "name": "session_id",
                "description": "The ID of the user's session",
                "required": False,
                "allowMultiple": False,
                "dataType": str.__name__,
                "paramType": "query"
            }
        ],
        responseMessages=[
            {
                "code": httplib.BAD_REQUEST,
                "message": "The database connection was not properly set up"
            }
        ]
    )
    #endregion
    def get(self):
        session_id = get_session_id(session, request)
        constraint_id = request.args.get('constraint_id', -1)

        dao = ThreatDAO(session_id)
        threats = dao.get_threats(constraint_id=constraint_id)

        resp = make_response(json_serialize(threats, session_id=session_id), httplib.OK)
        resp.contenttype = 'application/json'
        return resp

    # region Swagger Doc
    @swagger.operation(
        notes='Creates a new threat',
        nickname='threats-post',
        parameters=[
            {
                "name": "body",
                "description": "The serialized version of the new threat to be added",
                "required": True,
                "allowMultiple": False,
                "type": ThreatMessage.__name__,
                "paramType": "body"
            },
            {
                "name": "session_id",
                "description": "The ID of the user's session",
                "required": False,
                "allowMultiple": False,
                "dataType": str.__name__,
                "paramType": "query"
            }
        ],
        responseMessages=[
            {
                'code': httplib.BAD_REQUEST,
                'message': 'One or more attributes are missing'
            },
            {
                'code': httplib.CONFLICT,
                'message': 'Some problems were found during the name check'
            },
            {
                'code': httplib.CONFLICT,
                'message': 'A database error has occurred'
            }
        ]
    )
    # endregion
    def post(self):
        session_id = get_session_id(session, request)

        dao = ThreatDAO(session_id)
        new_vuln = dao.from_json(request)
        vuln_id = dao.add_threat(new_vuln)

        resp_dict = {'message': 'Threat successfully added', 'threat_id': vuln_id}
        resp = make_response(json_serialize(resp_dict), httplib.OK)
        resp.contenttype = 'application/json'
        return resp

class ThreatByIdAPI(Resource):
    # region Swagger Doc
    @swagger.operation(
        notes='Get a threat by ID',
        nickname='threat-by-id-get',
        responseClass=ThreatModel.__name__,
        parameters=[
            {
                "name": "session_id",
                "description": "The ID of the user's session",
                "required": False,
                "allowMultiple": False,
                "dataType": str.__name__,
                "paramType": "query"
            }
        ],
        responseMessages=[
            {
                "code": httplib.BAD_REQUEST,
                "message": "The database connection was not properly set up"
            }
        ]
    )
    # endregion
    def get(self, id):
        session_id = get_session_id(session, request)

        dao = ThreatDAO(session_id)
        threat = dao.get_threat_by_id(vuln_id=id)

        resp = make_response(json_serialize(threat, session_id=session_id), httplib.OK)
        resp.headers['Content-type'] = 'application/json'
        return resp

class ThreatByNameAPI(Resource):
    # region Swagger Doc
    @swagger.operation(
        notes='Get a threat by name',
        nickname='threat-by-name-get',
        responseClass=ThreatModel.__name__,
        parameters=[
            {
                "name": "session_id",
                "description": "The ID of the user's session",
                "required": False,
                "allowMultiple": False,
                "dataType": str.__name__,
                "paramType": "query"
            }
        ],
        responseMessages=[
            {
                "code": httplib.BAD_REQUEST,
                "message": "The database connection was not properly set up"
            }
        ]
    )
    # endregion
    def get(self, name):
        session_id = get_session_id(session, request)

        dao = ThreatDAO(session_id)
        threat = dao.get_threat_by_name(name=name)

        resp = make_response(json_serialize(threat, session_id=session_id), httplib.OK)
        resp.headers['Content-type'] = 'application/json'
        return resp

    # region Swagger Docs
    @swagger.operation(
        notes='Updates a threat',
        nickname='threat-by-name-put',
        parameters=[
            {
                'name': 'body',
                "description": "Options to be passed to the import tool",
                "required": True,
                "allowMultiple": False,
                'type': ThreatMessage.__name__,
                'paramType': 'body'
            },
            {
                "name": "session_id",
                "description": "The ID of the user's session",
                "required": False,
                "allowMultiple": False,
                "dataType": str.__name__,
                "paramType": "query"
            }
        ],
        responseMessages=[
            {
                'code': httplib.BAD_REQUEST,
                'message': 'The provided file is not a valid XML file'
            },
            {
                'code': httplib.BAD_REQUEST,
                'message': '''Some parameters are missing. Be sure 'threat' is defined.'''
            }
        ]
    )
    # endregion
    def put(self, name):
        session_id = get_session_id(session, request)

        dao = ThreatDAO(session_id)
        req = dao.from_json(request)
        dao.update_threat(req, name=name)

        resp_dict = {'message': 'Threat successfully updated'}
        resp = make_response(json_serialize(resp_dict), httplib.OK)
        resp.headers['Content-type'] = 'application/json'
        return resp

    # region Swagger Doc
    @swagger.operation(
        notes='Deletes an existing threat',
        nickname='threat-by-name-delete',
        parameters=[
            {
                "name": "session_id",
                "description": "The ID of the user's session",
                "required": False,
                "allowMultiple": False,
                "dataType": str.__name__,
                "paramType": "query"
            }
        ],
        responseMessages=[
            {
                'code': httplib.BAD_REQUEST,
                'message': 'One or more attributes are missing'
            },
            {
                'code': httplib.NOT_FOUND,
                'message': 'The provided threat name could not be found in the database'
            },
            {
                'code': httplib.CONFLICT,
                'message': 'Some problems were found during the name check'
            },
            {
                'code': httplib.CONFLICT,
                'message': 'A database error has occurred'
            }
        ]
    )
    # endregion
    def delete(self, name):
        session_id = get_session_id(session, request)

        dao = ThreatDAO(session_id)
        dao.delete_threat(name=name)

        resp_dict = {'message': 'Threat successfully deleted'}
        resp = make_response(json_serialize(resp_dict), httplib.OK)
        resp.headers['Content-type'] = 'application/json'
        return resp

class ThreatTypesAPI(Resource):
    #region Swagger Doc
    @swagger.operation(
        notes='Get all threats',
        nickname='threats-get',
        responseClass=ThreatModel.__name__,
        responseContainer='List',
        parameters=[
            {
                "name": "ordered",
                "description": "Defines if the list has to be order",
                "default": 1,
                "required": False,
                "allowMultiple": False,
                "dataType": int.__name__,
                "paramType": "query"
            },
            {
                "name": "session_id",
                "description": "The ID of the user's session",
                "required": False,
                "allowMultiple": False,
                "dataType": str.__name__,
                "paramType": "query"
            }
        ],
        responseMessages=[
            {
                "code": httplib.BAD_REQUEST,
                "message": "The database connection was not properly set up"
            }
        ]
    )
    #endregion
    def get(self):
        session_id = get_session_id(session, request)
        constraint_id = request.args.get('constraint_id', -1)

        dao = ThreatDAO(session_id)
        threats = dao.get_threat_types(constraint_id=constraint_id)

        resp = make_response(json_serialize(threats, session_id=session_id), httplib.OK)
        resp.contenttype = 'application/json'
        return resp