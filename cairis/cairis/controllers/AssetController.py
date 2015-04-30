import ARM
import httplib
from AssetModel import AssetModel
from AssetParameters import AssetParameters
from Borg import Borg
from CairisHTTPError import CairisHTTPError
from flask import request, session, make_response
from flask_restful_swagger import swagger
from flask.ext.restful import Resource
from tools.JsonConverter import json_serialize, json_deserialize
from tools.ModelDefinitions import AssetModel as SwaggerAssetModel
from tools.SessionValidator import validate_proxy, validate_fonts

__author__ = 'Robin Quetin'


class AssetsAPI(Resource):
    #region Swagger Doc
    @swagger.operation(
        notes='Get all assets',
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
            }
        ],
        responseMessages=[
            {
                "code": 400,
                "message": "The database connection was not properly set up"
            }
        ]
    )
    #endregion
    def get(self):
        session_id = request.args.get('session_id', None)
        db_proxy = validate_proxy(session, session_id)
        assets = db_proxy.getAssets()

        resp = make_response(json_serialize(assets, session_id=session_id))
        resp.headers['Content-Type'] = "application/json"
        return resp

    #region Swagger Doc
    @swagger.operation(
        notes='Creates a new asset',
        nickname='asset-post',
        parameters=[
            {
                "name": "body",
                "description": "The serialized version of the new asset to be added",
                "required": True,
                "allowMultiple": False,
                "type": SwaggerAssetModel.__name__,
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
    #endregion
    def post(self):
        session_id = request.args.get('session_id', None)
        db_proxy = validate_proxy(session, session_id)
        new_json_asset = request.get_json()
        asset = json_deserialize(new_json_asset, 'asset')

        try:
            db_proxy.nameCheck(asset.theName, 'asset')
        except ARM.ARMException, errorText:
            raise CairisHTTPError(httplib.CONFLICT, errorText.value, 'Database conflict')

        assetParams = AssetParameters(asset.theName, asset.theShortCode, asset.theDescription, asset.theSignificance,
                                      asset.theType, asset.isCritical, asset.theCriticalRationale, asset.theTags,
                                      asset.theInterfaces, asset.theEnvironmentProperties)

        try:
            resp_dict = dict()
            resp_dict['asset_id'] = db_proxy.addAsset(assetParams)
            resp = make_response(json_serialize(resp_dict), 200)
            resp.contenttype = 'application/json'
            return resp
        except ARM.ARMException, ex:
            raise CairisHTTPError(httplib.CONFLICT, ex.value, 'Database conflict')

class AssetByIdAPI(Resource):
    #region Swagger Doc
    @swagger.operation(
        notes='Get detailed information about an asset',
        responseClass=str.__name__,
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
                "code": 400,
                "message": "The database connection was not properly set up"
            }
        ]
    )
    #endregion
    def get(self, name):
        session_id = request.args.get('session_id', None)
        db_proxy = validate_proxy(session, session_id)
        assets = db_proxy.getAssets()
        found_asset = None

        if assets is not None:
            found_asset = assets.get(name, None)

        resp = make_response(json_serialize(found_asset, session_id=session_id))
        resp.headers['Content-Type'] = "application/json"
        return resp


class AssetNamesAPI(Resource):
    #region Swagger Doc
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
                "code": 400,
                "message": "The database connection was not properly set up"
            }
        ]
    )
    #endregion
    def get(self):
        session_id = request.args.get('session_id', None)
        db_proxy = validate_proxy(session, session_id)
        assets = db_proxy.getDimensionNames('asset')

        resp = make_response(json_serialize(assets, session_id=session_id))
        resp.headers['Content-Type'] = "application/json"
        return resp


class AssetModelAPI(Resource):
    #region Swagger Doc
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
                "code": 400,
                "message": "The database connection was not properly set up"
            }
        ]
    )
    #endregion
    def get(self):
        b = Borg()
        model_generator = b.model_generator

        session_id = request.args.get('session_id', None)
        environment = request.args.get('environment', None)

        if environment is None:
            raise CairisHTTPError(405, message='Environment not defined')

        db_proxy = validate_proxy(session, session_id)
        fontName, fontSize, apFontName = validate_fonts(session, session_id)
        associationDictionary = db_proxy.classModel(environment)
        associations = AssetModel(associationDictionary.values(), environment, db_proxy=db_proxy, fontName=fontName,
            fontSize=fontSize)
        dot_code = associations.graph()

        resp = make_response(model_generator.generate(dot_code), 200)
        accept_header = request.headers.get('Accept', 'image/svg+xml')
        if accept_header.find('text/plain') > -1:
            resp.headers['Content-type'] = 'text/plain'
        else:
            resp.headers['Content-type'] = 'image/svg+xml'

        return resp