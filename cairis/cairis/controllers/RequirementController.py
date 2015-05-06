import httplib

from CairisHTTPError import MalformedJSONHTTPError, MissingParameterHTTPError, handle_exception
from flask import session, request, make_response

from flask.ext.restful import Resource
from flask.ext.restful_swagger import swagger
from Requirement import Requirement
from tools.ModelDefinitions import RequirementModel
from tools.SessionValidator import validate_proxy
from tools.JsonConverter import json_serialize, json_deserialize


__author__ = 'Robin Quetin'


class RequirementsAPI(Resource):
    # region Swagger Doc
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
                "code": httplib.BAD_REQUEST,
                "message": "The database connection was not properly set up"
            }
        ]
    )
    # endregion
    def get(self):
        session_id = request.args.get('session_id', None)
        ordered = request.args.get('ordered', 1)
        db_proxy = validate_proxy(session, session_id)

        if ordered == 1:
            reqs = db_proxy.getOrderedRequirements('', 1)
        else:
            reqs = db_proxy.getRequirements('', 1)

        resp = make_response(json_serialize(reqs, session_id=session_id), httplib.OK)
        resp.headers['Content-type'] = 'application/json'
        resp.headers['Access-Control-Allow-Origin'] = "*"
        return resp

    # region Swagger Doc
    @swagger.operation(
        notes='Creates a new requirement',
        nickname='requirements-post',
        parameters=[
            {
                "name": "body",
                "description": "The serialized version of the new requirement to be added",
                "required": True,
                "allowMultiple": False,
                "type": RequirementModel.__name__,
                "paramType": "body"
            },
            {
                "name": "asset",
                "description": "The name of the asset which is associated to the new requirement",
                "required": False,
                "allowMultiple": False,
                "dataType": str.__name__,
                "paramType": "query"
            },
            {
                "name": "environment",
                "description": "The name of the environment which is associated to the new requirement",
                "required": False,
                "allowMultiple": False,
                "dataType": str.__name__,
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
        session_id = request.args.get('session_id', None)
        asset_name = request.args.get('asset', None)
        environment_name = request.args.get('environment', None)
        json_new_req = request.get_json(silent=True)
        db_proxy = validate_proxy(session, session_id)

        if json_new_req is False:
            raise MalformedJSONHTTPError()

        new_req = json_deserialize(json_new_req)

        if asset_name is not None:
            try:
                db_proxy.addRequirement(new_req, assetName=asset_name, isAsset=True)
            except Exception as ex:
                handle_exception(ex)
        elif environment_name is not None:
            try:
                db_proxy.addRequirement(new_req, assetName=environment_name, isAsset=False)
            except Exception as ex:
                handle_exception(ex)
        else:
            raise MissingParameterHTTPError(param_names=['asset', 'environment'])

        resp = make_response('Successfully added new requirement', httplib.OK)
        resp.contenttype = 'text/plain'
        return resp


class RequirementsByAssetAPI(Resource):
    # region Swagger Doc
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
                "code": httplib.BAD_REQUEST,
                "message": "The database connection was not properly set up"
            }
        ]
    )
    # endregion
    def get(self, name):
        session_id = request.args.get('session_id', None)
        ordered = request.args.get('ordered', 1)
        db_proxy = validate_proxy(session, session_id)

        if ordered == 1:
            try:
                reqs = db_proxy.getOrderedRequirements(name, 1)
            except Exception as ex:
                handle_exception(ex)
        else:
            try:
                reqs = db_proxy.getRequirements(name, 1)
            except Exception as ex:
                handle_exception(ex)

        resp = make_response(json_serialize(reqs, session_id=session_id), httplib.OK)
        resp.headers['Content-type'] = 'application/json'
        return resp


class RequirementsByEnvironmentAPI(Resource):
    # region Swagger Doc
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
                "code": httplib.BAD_REQUEST,
                "message": "The database connection was not properly set up"
            }
        ]
    )
    # endregion
    def get(self, name):
        session_id = request.args.get('session_id', None)
        ordered = request.args.get('ordered', 1)
        db_proxy = validate_proxy(session, session_id)

        if ordered == 1:
            try:
                reqs = db_proxy.getOrderedRequirements(name, 0)
            except Exception as ex:
                handle_exception(ex)
        else:
            try:
                reqs = db_proxy.getRequirements(name, 0)
            except Exception as ex:
                handle_exception(ex)

        resp = make_response(json_serialize(reqs, session_id=session_id), httplib.OK)
        resp.headers['Content-type'] = 'application/json'
        return resp


class RequirementByIdAPI(Resource):
    # region Swagger Doc
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
                "code": httplib.BAD_REQUEST,
                "message": "The database connection was not properly set up"
            }
        ]
    )
    # endregion
    def get(self, id):
        session_id = request.args.get('session_id', None)
        db_proxy = validate_proxy(session, session_id)

        try:
            req = db_proxy.getRequirement(id)
        except Exception as ex:
            handle_exception(ex)

        resp = make_response(json_serialize(req, session_id=session_id), httplib.OK)
        resp.headers['Content-type'] = 'application/json'
        return resp


class RequirementUpdateAPI(Resource):
    # region Swagger Docs
    @swagger.operation(
        notes='Imports data from an XML file',
        nickname='asset-model-get',
        parameters=[
            {
                'name': 'body',
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
                'code': httplib.BAD_REQUEST,
                'message': 'The provided file is not a valid XML file'
            },
            {
                'code': httplib.BAD_REQUEST,
                'message': '''Some parameters are missing. Be sure 'requirement' is defined.'''
            }
        ]
    )
    # endregion
    def put(self):
        session_id = request.args.get('session_id', None)
        json_dict = request.get_json(silent=True)
        db_proxy = validate_proxy(session, session_id)

        if json_dict is False:
            raise MalformedJSONHTTPError()
        json_string = json_serialize(json_dict)

        reqObj = json_deserialize(json_string, 'requirement')
        if not isinstance(reqObj, Requirement):
            raise MissingParameterHTTPError()

        reqObj.incrementVersion()

        try:
            db_proxy.updateRequirement(reqObj)
        except Exception as ex:
            handle_exception(ex)

        resp = make_response('Requirement successfully updated', httplib.OK)
        resp.headers['Content-type'] = 'text/plain'
        return resp