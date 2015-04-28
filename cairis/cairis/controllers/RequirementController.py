from flask import session, request, make_response
from flask.ext.restful import Resource
from flask.ext.restful_swagger import swagger
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
        responseClass=Requirement.__name__,
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
        return resp

class FilteredRequirementsAPI(Resource):
    @swagger.operation(
        notes='Get the filtered requirements',
        nickname='requirements-filtered-get',
        responseClass=Requirement.__name__,
        responseContainer='List',
        parameters=[
            {
                "name": "is_asset",
                "description": "Defines if the filter is an asset filter",
                "required": False,
                "default": 1,
                "allowMultiple": False,
                "dataType": int.__name__,
                "paramType": "query"
            },
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
    def get(self, filter):
        session_id = request.args.get('session_id', None)
        is_asset = request.args.get('is_asset', 1)
        ordered = request.args.get('ordered', 1)
        db_proxy = validate_proxy(session, session_id)

        if ordered == 1:
            reqs = db_proxy.getOrderedRequirements(filter, is_asset==1)
        else:
            reqs = db_proxy.getRequirements(filter, is_asset)

        resp = make_response(json_serialize(reqs, session_id=session_id), 200)
        resp.headers['Content-type'] = 'application/json'
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
        json_dict = request.get_json()
        db_proxy = validate_proxy(session, session_id)

        reqObj = json_deserialize(json_dict, 'requirement')
        db_proxy.updateRequirement(reqObj)

        resp = make_response('Requirement successfully updated', 200)
        resp.headers['Content-type'] = 'text/plain'
        return resp