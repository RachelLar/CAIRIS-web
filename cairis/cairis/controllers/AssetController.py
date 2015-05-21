import httplib

from flask import request, session, make_response
from flask_restful_swagger import swagger
from flask.ext.restful import Resource

from AssetModel import AssetModel
from Borg import Borg
from CairisHTTPError import ObjectNotFoundHTTPError, MissingParameterHTTPError
from data.AssetDAO import AssetDAO
from tools.JsonConverter import json_serialize
from tools.MessageDefinitions import AssetMessage, AssetEnvironmentPropertiesMessage
from tools.ModelDefinitions import AssetModel as SwaggerAssetModel, AssetEnvironmentPropertiesModel
from tools.SessionValidator import validate_proxy, validate_fonts, get_session_id


class AssetsAPI(Resource):
    # region Swagger Doc
    @swagger.operation(
        notes='Get all assets without the asset environment properties.' +
              'To get the asset environment properties of an asset, please use /api/assets/{name}/properties',
        responseClass=SwaggerAssetModel.__name__,
        nickname='assets-get',
        parameters=[
            {
                "name": "session_id",
                "description": "The ID of the user's session",
                "required": False,
                "allowMultiple": False,
                "dataType": str.__name__,
                "paramType": "query"
            },
            {
                "name": "constraint_id",
                "description": "An ID used to filter the assets",
                "required": False,
                "default": -1,
                "allowMultiple": False,
                "dataType": int.__name__,
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
        constraint_id = request.args.get('constraint_id', -1)
        session_id = get_session_id(session, request)
        dao = AssetDAO(session_id)
        assets = dao.get_assets(constraint_id=constraint_id)

        resp = make_response(json_serialize(assets, session_id=session_id))
        resp.headers['Content-Type'] = "application/json"
        return resp

    # region Swagger Doc
    @swagger.operation(
        notes='Creates a new asset',
        nickname='asset-post',
        parameters=[
            {
                "name": "body",
                "description": "The serialized version of the new asset to be added",
                "required": True,
                "allowMultiple": False,
                "type": AssetMessage.__name__,
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

        dao = AssetDAO(session_id)
        asset, props = dao.from_json(request)
        new_id = dao.add_asset(asset, props)

        resp_dict = {'asset_id': new_id}
        resp = make_response(json_serialize(resp_dict), httplib.OK)
        resp.contenttype = 'application/json'
        return resp


class AssetByNameAPI(Resource):
    # region Swagger Doc
    @swagger.operation(
        notes='Get an asset by name',
        responseClass=SwaggerAssetModel.__name__,
        nickname='asset-by-name-get',
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

        dao = AssetDAO(session_id)
        found_asset = dao.get_asset_by_name(name)

        resp = make_response(json_serialize(found_asset, session_id=session_id))
        resp.headers['Content-Type'] = "application/json"
        return resp

    # region Swagger Doc
    @swagger.operation(
        notes='Updates an existing asset',
        nickname='asset-put',
        parameters=[
            {
                "name": "body",
                "description": "The session ID and the serialized version of the asset to be updated",
                "required": True,
                "allowMultiple": False,
                "type": AssetMessage.__name__,
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
                'code': httplib.NOT_FOUND,
                'message': 'The provided asset name could not be found in the database'
            },
            {
                'code': httplib.CONFLICT,
                'message': 'A database error has occurred'
            }
        ]
    )
    # endregion
    def put(self, name):
        session_id = get_session_id(session, request)

        dao = AssetDAO(session_id)
        asset, props = dao.from_json(request)
        dao.update_asset(asset, name=name, asset_props=props)

        resp_dict = {'message': 'Update successful'}
        resp = make_response(json_serialize(resp_dict), httplib.OK)
        resp.contenttype = 'application/json'
        return resp

    # region Swagger Doc
    @swagger.operation(
        notes='Deletes an existing asset',
        nickname='asset-delete',
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
                'code': httplib.CONFLICT,
                'message': 'Some problems were found during the name check'
            },
            {
                'code': httplib.NOT_FOUND,
                'message': 'The provided asset name could not be found in the database'
            },
            {
                'code': httplib.CONFLICT,
                'message': 'A database error has occurred'
            }
        ]
    )
    # endregion
    def delete(self, name):
        session_id = request.args.get('session_id', None)
        dao = AssetDAO(session_id)

        dao.delete_asset(name=name)

        resp_dict = {'message': 'Asset successfully deleted'}
        resp = make_response(json_serialize(resp_dict), httplib.OK)
        resp.contenttype = 'application/json'
        return resp

class AssetByIdAPI(Resource):
    # region Swagger Doc
    @swagger.operation(
        notes='Get an asset by ID',
        responseClass=SwaggerAssetModel.__name__,
        nickname='asset-by-id-get',
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

        dao = AssetDAO(session_id)
        asset = dao.get_asset_by_id(id)
        if asset is None:
            raise ObjectNotFoundHTTPError('The asset')

        resp = make_response(json_serialize(asset, session_id=session_id))
        resp.headers['Content-Type'] = "application/json"
        return resp


class AssetNamesAPI(Resource):
    # region Swagger Doc
    @swagger.operation(
        notes='Get a list of assets',
        responseClass=str.__name__,
        responseContainer="List",
        nickname='asset-names-get',
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
    def get(self):
        session_id = request.args.get('session_id', None)
        db_proxy = validate_proxy(session, session_id)
        assets = db_proxy.getDimensionNames('asset')

        resp = make_response(json_serialize(assets, session_id=session_id))
        resp.headers['Content-Type'] = "application/json"
        return resp


class AssetModelAPI(Resource):
    # region Swagger Doc
    @swagger.operation(
        notes='Get the asset model for a specific environment',
        nickname='asset-model-get',
        parameters=[
            {
                "name": "environment",
                "description": "The environment to be used for the asset model",
                "required": True,
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
                "code": httplib.BAD_REQUEST,
                "message": "The database connection was not properly set up"
            }
        ]
    )
    # endregion
    def get(self):
        b = Borg()
        model_generator = b.model_generator

        session_id = request.args.get('session_id', None)
        environment = request.args.get('environment', None)

        if environment is None:
            raise MissingParameterHTTPError(param_names=['environment'])

        db_proxy = validate_proxy(session, session_id)
        fontName, fontSize, apFontName = validate_fonts(session, session_id)
        associationDictionary = db_proxy.classModel(environment)
        associations = AssetModel(associationDictionary.values(), environment, db_proxy=db_proxy, fontName=fontName,
            fontSize=fontSize)
        dot_code = associations.graph()

        resp = make_response(model_generator.generate(dot_code), httplib.OK)
        accept_header = request.headers.get('Accept', 'image/svg+xml')
        if accept_header.find('text/plain') > -1:
            resp.headers['Content-type'] = 'text/plain'
        else:
            resp.headers['Content-type'] = 'image/svg+xml'

        return resp


class AssetEnvironmentPropertiesAPI(Resource):
    # region Swagger Doc
    @swagger.operation(
        notes='Get the environment properties for a specific asset',
        nickname='asset-envprops-by-name-get',
        responseClass=AssetEnvironmentPropertiesModel.__name__,
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
    def get(self, asset_name):
        session_id = get_session_id(session, request)

        dao = AssetDAO(session_id)
        asset_props = dao.get_asset_props(name=asset_name)

        resp = make_response(json_serialize(asset_props, session_id=session_id))
        resp.contenttype = 'application/json'
        return resp

    # region Swagger Doc
    @swagger.operation(
        notes='Updates the environment properties for a specific asset',
        nickname='asset-envprops-by-name-put',
        parameters=[
            {
                "name": "body",
                "required": True,
                "allowMultiple": False,
                "dataType": AssetEnvironmentPropertiesMessage.__name__,
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
                "code": httplib.BAD_REQUEST,
                "message": "The database connection was not properly set up"
            }
        ]
    )
    # endregion
    def put(self, asset_name):
        session_id = get_session_id(session, request)

        dao = AssetDAO(session_id)
        asset, asset_prop = dao.from_json(request, to_props=True)
        dao.update_asset_properties(asset_prop, name=asset_name)

        resp_dict = {'message': 'The asset properties were successfully updated.'}
        resp = make_response(json_serialize(resp_dict), httplib.OK)
        resp.contenttype = 'application/json'
        return resp