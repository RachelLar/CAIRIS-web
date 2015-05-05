import ARM
import httplib
from Asset import Asset
from AssetEnvironmentProperties import AssetEnvironmentProperties
from AssetModel import AssetModel
from AssetParameters import AssetParameters
from Borg import Borg
from CairisHTTPError import CairisHTTPError
from flask import request, session, make_response
from flask_restful_swagger import swagger
from flask.ext.restful import Resource
import armid
from tools.JsonConverter import json_serialize, json_deserialize
from tools.ModelDefinitions import AssetModel as SwaggerAssetModel
from tools.SessionValidator import validate_proxy, validate_fonts

__author__ = 'Robin Quetin'


class AssetsAPI(Resource):
    # region Swagger Doc
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
    # endregion
    def get(self):
        session_id = request.args.get('session_id', None)
        db_proxy = validate_proxy(session, session_id)
        assets = db_proxy.getAssets()

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
    # endregion
    def post(self):
        session_id = request.args.get('session_id', None)
        db_proxy = validate_proxy(session, session_id)
        new_json_asset = request.get_json(silent=True)

        if new_json_asset is False:
            raise CairisHTTPError(httplib.BAD_REQUEST,
                                  'The request body could not be converted to a JSON object.' +
                                  '''Check if the request content type is 'application/json' ''' +
                                  'and that the JSON string is well-formed',
                                  'Unreadable JSON data')

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

class AssetByNameAPI(Resource):
    # region Swagger Doc
    @swagger.operation(
        notes='Get detailed information about an asset',
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
                "code": 400,
                "message": "The database connection was not properly set up"
            }
        ]
    )
    # endregion
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

class AssetByIdAPI(Resource):
    # region Swagger Doc
    @swagger.operation(
        notes='Get detailed information about an asset',
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
                "code": 400,
                "message": "The database connection was not properly set up"
            }
        ]
    )
    # endregion
    def get(self, id):
        session_id = request.args.get('session_id', None)
        db_proxy = validate_proxy(session, session_id)
        assets = db_proxy.getAssets()
        found_asset = None
        idx = 0

        while found_asset is None and idx < len(assets):
            if assets.values()[idx].theId == id:
                found_asset = assets.values()[idx]
            idx += 1

        resp = make_response(json_serialize(found_asset, session_id=session_id))
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
                "code": 400,
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
                "code": 400,
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

class AssetEnvironmentPropertiesAPI(Resource):
    @swagger.operation(
        notes='Get the environment properties for a specific asset',
        nickname='asset-envprops-by-id-get',
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
    # endregion
    def get(self, asset_id):
        session_id = request.args.get('session_id', None)
        db_proxy = validate_proxy(session, session_id)

        assets = db_proxy.getAssets()
        if len(assets) > 0:
            assets = assets.values()
        else:
            raise CairisHTTPError(status_code=httplib.NOT_FOUND,
                                  message='There were no Assets found in the database.',
                                  status='No assets found')

        found_asset = None
        idx = 0

        while found_asset is None and idx < len(assets):
            if assets[idx].theId == asset_id:
                found_asset = assets[idx]
            idx += 1

        if not isinstance(found_asset, Asset):
            raise CairisHTTPError(status_code=httplib.CONFLICT,
                                  message='There is no asset in the database with the specified ID',
                                  status='Asset not found')

        if found_asset is None:
            raise CairisHTTPError(status_code=httplib.CONFLICT,
                                  message='There is no asset in the database with the specified ID',
                                  status='Asset not found')
        else:
            values = ['None', 'Low', 'Medium', 'High']
            envPropertiesDict = dict()
            for envProperty in found_asset.theEnvironmentProperties:
                assert isinstance(envProperty, AssetEnvironmentProperties)
                envPropertyDict = envPropertiesDict.get(envProperty.theEnvironmentName, dict())
                syProperties = envProperty.properties()
                pRationale = envProperty.rationale()
                cProperty = syProperties[armid.C_PROPERTY]
                cRationale = pRationale[armid.C_PROPERTY]
                if (cProperty != armid.NONE_VALUE):
                    prop_name = 'Confidentiality'
                    envPropertyDict[prop_name] = dict()
                    envPropertyDict[prop_name]['value'] = values[cProperty]
                    envPropertyDict[prop_name]['rationale'] = cRationale

                iProperty = syProperties[armid.I_PROPERTY]
                iRationale = pRationale[armid.I_PROPERTY]
                if (iProperty != armid.NONE_VALUE):
                    prop_name = 'Integrity'
                    envPropertyDict[prop_name] = dict()
                    envPropertyDict[prop_name]['value'] = values[iProperty]
                    envPropertyDict[prop_name]['rationale'] = iRationale

                avProperty = syProperties[armid.AV_PROPERTY]
                avRationale = pRationale[armid.AV_PROPERTY]
                if (avProperty != armid.NONE_VALUE):
                    prop_name = 'Availability'
                    envPropertyDict[prop_name] = dict()
                    envPropertyDict[prop_name]['value'] = values[avProperty]
                    envPropertyDict[prop_name]['rationale'] = avRationale

                acProperty = syProperties[armid.AC_PROPERTY]
                acRationale = pRationale[armid.AC_PROPERTY]
                if (acProperty != armid.NONE_VALUE):
                    prop_name = 'Accountability'
                    envPropertyDict[prop_name] = dict()
                    envPropertyDict[prop_name]['value'] = values[acProperty]
                    envPropertyDict[prop_name]['rationale'] = acRationale

                anProperty = syProperties[armid.AN_PROPERTY]
                anRationale = pRationale[armid.AN_PROPERTY]
                if (anProperty != armid.NONE_VALUE):
                    prop_name = 'Anonymity'
                    envPropertyDict[prop_name] = dict()
                    envPropertyDict[prop_name]['value'] = values[anProperty]
                    envPropertyDict[prop_name]['rationale'] = anRationale

                panProperty = syProperties[armid.PAN_PROPERTY]
                panRationale = pRationale[armid.PAN_PROPERTY]
                if (panProperty != armid.NONE_VALUE):
                    prop_name = 'Pseudonymity'
                    envPropertyDict[prop_name] = dict()
                    envPropertyDict[prop_name]['value'] = values[panProperty]
                    envPropertyDict[prop_name]['rationale'] = panRationale

                unlProperty = syProperties[armid.UNL_PROPERTY]
                unlRationale = pRationale[armid.UNL_PROPERTY]
                if (unlProperty != armid.NONE_VALUE):
                    prop_name = 'Unlinkability'
                    envPropertyDict[prop_name] = dict()
                    envPropertyDict[prop_name]['value'] = values[unlProperty]
                    envPropertyDict[prop_name]['rationale'] = unlRationale

                unoProperty = syProperties[armid.UNO_PROPERTY]
                unoRationale = pRationale[armid.UNO_PROPERTY]
                if (unoProperty != armid.NONE_VALUE):
                    prop_name = 'Unobservability'
                    envPropertyDict[prop_name] = dict()
                    envPropertyDict[prop_name]['value'] = values[unoProperty]
                    envPropertyDict[prop_name]['rationale'] = unoRationale

                envPropertiesDict[envProperty.theEnvironmentName] = envPropertyDict

            resp = make_response(json_serialize(envPropertiesDict))
            resp.contenttype = 'application/json'
            return resp
