import httplib
from flask import request, session, make_response
from flask.ext.restful import Resource
from flask_restful_swagger import swagger
from data.AttackerDAO import AttackerDAO
from tools.JsonConverter import json_serialize
from tools.MessageDefinitions import AttackerMessage
from tools.ModelDefinitions import AttackerModel
from tools.SessionValidator import get_session_id

__author__ = 'Robin Quetin'


class AttackersAPI(Resource):
    #region Swagger Doc
    @swagger.operation(
        notes='Get all attackers',
        nickname='attackers-get',
        responseClass=AttackerModel.__name__,
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

        dao = AttackerDAO(session_id)
        attackers = dao.get_attackers(constraint_id=constraint_id)

        resp = make_response(json_serialize(attackers, session_id=session_id), httplib.OK)
        resp.contenttype = 'application/json'
        return resp

    # region Swagger Doc
    @swagger.operation(
        notes='Creates a new attacker',
        nickname='attackers-post',
        parameters=[
            {
                "name": "body",
                "description": "The serialized version of the new attacker to be added",
                "required": True,
                "allowMultiple": False,
                "type": AttackerMessage.__name__,
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

        dao = AttackerDAO(session_id)
        new_attacker = dao.from_json(request)
        attacker_id = dao.add_attacker(new_attacker)

        resp_dict = {'message': 'Attacker successfully added', 'attacker_id': attacker_id}
        resp = make_response(json_serialize(resp_dict), httplib.OK)
        resp.contenttype = 'application/json'
        return resp

class AttackerByNameAPI(Resource):
    # region Swagger Doc
    @swagger.operation(
        notes='Get a attacker by name',
        nickname='attacker-by-name-get',
        responseClass=AttackerModel.__name__,
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

        dao = AttackerDAO(session_id)
        attacker = dao.get_attacker_by_name(name=name)

        resp = make_response(json_serialize(attacker, session_id=session_id), httplib.OK)
        resp.headers['Content-type'] = 'application/json'
        return resp

    # region Swagger Docs
    @swagger.operation(
        notes='Updates a attacker',
        nickname='attacker-by-name-put',
        parameters=[
            {
                'name': 'body',
                "description": "JSON serialized version of the attacker to be updated",
                "required": True,
                "allowMultiple": False,
                'type': AttackerMessage.__name__,
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
                'message': '''Some parameters are missing. Be sure 'attacker' is defined.'''
            }
        ]
    )
    # endregion
    def put(self, name):
        session_id = get_session_id(session, request)

        dao = AttackerDAO(session_id)
        req = dao.from_json(request)
        dao.update_attacker(req, name=name)

        resp_dict = {'message': 'Attacker successfully updated'}
        resp = make_response(json_serialize(resp_dict), httplib.OK)
        resp.headers['Content-type'] = 'application/json'
        return resp

    # region Swagger Doc
    @swagger.operation(
        notes='Deletes an existing attacker',
        nickname='attacker-by-name-delete',
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
                'message': 'The provided attacker name could not be found in the database'
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

        dao = AttackerDAO(session_id)
        dao.delete_attacker(name=name)

        resp_dict = {'message': 'Attacker successfully deleted'}
        resp = make_response(json_serialize(resp_dict), httplib.OK)
        resp.headers['Content-type'] = 'application/json'
        return resp