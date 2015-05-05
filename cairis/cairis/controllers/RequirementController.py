import httplib
from flask import session, request, make_response, Blueprint
from flask.ext.restful import Resource, Api
from flask.ext.restful_swagger import swagger
from CairisHTTPError import CairisHTTPError
from Requirement import Requirement
from tools.ModelDefinitions import RequirementModel
from tools.SessionValidator import validate_proxy
from tools.JsonConverter import json_serialize, json_deserialize

__author__ = 'Robin Quetin'


# noinspection PyMethodMayBeStatic
class RequirementsAPI(Resource):
    @swagger.operation(
        notes='Get all requirements',
        nickname='requirements-get',
        responseClass=RequirementModel.__name__,
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
                "code": 400,
                "message": "The database connection was not properly set up"
            }
        ]
    )
    def get(self):
        session_id = request.args.get('session_id', None)
        ordered = request.args.get('ordered', 1)
        db_proxy = validate_proxy(session, session_id)

        if ordered == 1:
            reqs = db_proxy.getOrderedRequirements('', 1)
        else:
            reqs = db_proxy.getRequirements('', 1)

        resp = make_response(json_serialize(reqs, session_id=session_id), 200)
        resp.headers['Content-type'] = 'application/json'
        resp.headers['Access-Control-Allow-Origin'] = "*"
        return resp

class RequirementsByAssetAPI(Resource):
    @swagger.operation(
        notes='Get the requirements associated with an asset',
        nickname='requirements-by-asset-get',
        responseClass=RequirementModel.__name__,
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
                "code": 400,
                "message": "The database connection was not properly set up"
            }
        ]
    )
    def get(self, name):
        session_id = request.args.get('session_id', None)
        ordered = request.args.get('ordered', 1)
        db_proxy = validate_proxy(session, session_id)

        if ordered == 1:
            reqs = db_proxy.getOrderedRequirements(name, 1)
        else:
            reqs = db_proxy.getRequirements(name, 1)

        resp = make_response(json_serialize(reqs, session_id=session_id), 200)
        resp.headers['Content-type'] = 'application/json'
        resp.headers['Access-Control-Allow-Origin'] = "*"
        return resp

class RequirementsByEnvironmentAPI(Resource):
    @swagger.operation(
        notes='Get the requirements associated with an environment',
        nickname='requirements-by-environment-get',
        responseClass=RequirementModel.__name__,
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
                "code": 400,
                "message": "The database connection was not properly set up"
            }
        ]
    )
    def get(self, name):
        session_id = request.args.get('session_id', None)
        ordered = request.args.get('ordered', 1)
        db_proxy = validate_proxy(session, session_id)

        if ordered == 1:
            reqs = db_proxy.getOrderedRequirements(name, 0)
        else:
            reqs = db_proxy.getRequirements(name, 0)

        resp = make_response(json_serialize(reqs, session_id=session_id), 200)
        resp.headers['Content-type'] = 'application/json'
        resp.headers['Access-Control-Allow-Origin'] = "*"
        return resp

class RequirementByIdAPI(Resource):
    @swagger.operation(
        notes='Get a requirement by ID',
        nickname='requirement-by-id-get',
        responseClass=Requirement.__name__,
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
                "code": 400,
                "message": "The database connection was not properly set up"
            }
        ]
    )
    def get(self, id):
        session_id = request.args.get('session_id', None)
        db_proxy = validate_proxy(session, session_id)

        req = db_proxy.getRequirement(id)

        resp = make_response(json_serialize(req, session_id=session_id), 200)
        resp.headers['Content-type'] = 'application/json'
        resp.headers['Access-Control-Allow-Origin'] = "*"
        return resp

class RequirementUpdateAPI(Resource):
    @swagger.operation(
        notes='Imports data from an XML file',
        nickname='asset-model-get',
        parameters=[
            {
                'name':'body',
                "description": "Options to be passed to the import tool",
                "required": True,
                "allowMultiple": False,
                'type': RequirementModel.__name__,
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
                'code': 400,
                'message': 'The provided file is not a valid XML file'
            },
            {
                'code': 405,
                'message': '''Some parameters are missing. Be sure 'requirement' is defined.'''
            }
        ]
    )
    def put(self):
        session_id = request.args.get('session_id', None)
        json_dict = request.get_json(silent=True)
        db_proxy = validate_proxy(session, session_id)

        if json_dict is False:
            raise CairisHTTPError(httplib.BAD_REQUEST,
                                  'The request body could not be converted to a JSON object.' +
                                  '''Check if the request content type is 'application/json' ''' +
                                  'and that the JSON string is well-formed',
                                  'Unreadable JSON data')

        reqObj = json_deserialize(json_dict, 'requirement')
        db_proxy.updateRequirement(reqObj)

        resp = make_response('Requirement successfully updated', 200)
        resp.headers['Content-type'] = 'text/plain'
        return resp