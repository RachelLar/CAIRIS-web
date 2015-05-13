import httplib
import collections
import logging

from flask import request, session, make_response
from flask_restful_swagger import swagger
from flask.ext.restful import Resource
import numpy
from numpy.core.multiarray import array

import ARM
import armid
from Asset import Asset
from AssetEnvironmentProperties import AssetEnvironmentProperties
from AssetModel import AssetModel
from AssetParameters import AssetParameters
from Borg import Borg
from CairisHTTPError import MalformedJSONHTTPError, ARMHTTPError, CairisHTTPError, SilentHTTPError, \
    ObjectNotFoundHTTPError
from tools.JsonConverter import json_serialize, json_deserialize
from tools.MessageDefinitions import AssetMessage, AssetEnvironmentPropertiesMessage
from tools.ModelDefinitions import AssetModel as SwaggerAssetModel, AssetEnvironmentPropertiesModel, \
    AssetSecurityAttribute
from tools.SessionValidator import validate_proxy, validate_fonts


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
        session_id = request.args.get('session_id', None)
        db_proxy = validate_proxy(session, session_id)
        constraint_id = request.args.get('constraint_id', -1)
        assets = db_proxy.getAssets(constraint_id)

        for key in assets:
            assets[key].theEnvironmentDictionary = {}
            assets[key].theAssetPropertyDictionary = {}
            assets[key].theEnvironmentProperties = []

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
        session_id = request.args.get('session_id', None)
        new_json_message = request.get_json(silent=True)

        if new_json_message is False or new_json_message is None:
            raise MalformedJSONHTTPError()

        session_id = new_json_message.get('session_id', session_id)
        new_json_asset = json_serialize(new_json_message['object'])
        db_proxy = validate_proxy(session, session_id)
        asset = json_deserialize(new_json_asset, 'asset')

        try:
            db_proxy.nameCheck(asset.theName, 'asset')
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)

        assetParams = AssetParameters(asset.theName, asset.theShortCode, asset.theDescription, asset.theSignificance,
                                      asset.theType, asset.isCritical, asset.theCriticalRationale, asset.theTags,
                                      asset.theInterfaces, [])

        try:
            resp_dict = dict()
            resp_dict['asset_id'] = db_proxy.addAsset(assetParams)
            resp = make_response(json_serialize(resp_dict), httplib.OK)
            resp.contenttype = 'application/json'
            return resp
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)


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
                "code": httplib.BAD_REQUEST,
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

        if found_asset is None:
            raise ObjectNotFoundHTTPError(obj='The provided asset name')

        assert isinstance(found_asset, Asset)
        found_asset.theEnvironmentDictionary = {}
        found_asset.theEnvironmentProperties = []
        found_asset.theAssetPropertyDictionary = {}

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
        session_id = request.args.get('session_id', None)
        new_json_asset = request.get_json(silent=True)

        if new_json_asset is False or new_json_asset is None:
            b = Borg()
            b.logger.debug('Body: '+request.get_data())
            raise MalformedJSONHTTPError()

        session_id = new_json_asset.get('session_id', session_id)
        db_proxy = validate_proxy(session, session_id)
        asset = json_deserialize(new_json_asset['object'], 'asset')

        try:
            db_proxy.nameCheck(name, 'asset')
            raise CairisHTTPError(
                status_code=httplib.NOT_FOUND,
                message='The provided asset name could not be found in the database'
            )
        except ARM.ARMException as ex:
            if str(ex.value).find(' already exists') < 0:
                raise ARMHTTPError(ex)

        assetParams = AssetParameters(asset.theName, asset.theShortCode, asset.theDescription, asset.theSignificance,
                                      asset.theType, asset.isCritical, asset.theCriticalRationale, asset.theTags,
                                      asset.theInterfaces, asset.theEnvironmentProperties)
        assetParams.setId(asset.theId)

        try:
            db_proxy.updateAsset(assetParams)
            resp = make_response('Update successful', httplib.OK)
            resp.contenttype = 'text/plain'
            return resp
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)

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
        db_proxy = validate_proxy(session, session_id)
        assets = db_proxy.getAssets()
        found_asset = None

        if assets is not None:
            found_asset = assets.get(name, None)

        if found_asset is None or not isinstance(found_asset, Asset):
            raise CairisHTTPError(
                status_code=httplib.NOT_FOUND,
                message='The provided asset name could not be found in the database',
            )

        db_proxy.deleteAsset(found_asset.theId)


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
                "code": httplib.BAD_REQUEST,
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

        if found_asset is None:
            raise ObjectNotFoundHTTPError('The provided asset ID')

        assert isinstance(found_asset, Asset)
        found_asset.theEnvironmentDictionary = {}
        found_asset.theEnvironmentProperties = []
        found_asset.theAssetPropertyDictionary = {}

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
            raise CairisHTTPError(
                status_code=405,
                message='Environment not defined'
            )

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
        session_id = request.args.get('session_id', None)
        db_proxy = validate_proxy(session, session_id)

        assets = db_proxy.getAssets()
        if len(assets) > 0:
            assets = assets.values()
        else:
            raise CairisHTTPError(
                status_code=httplib.NOT_FOUND,
                message='There were no Assets found in the database.',
                status='No assets found'
            )

        found_asset = None
        idx = 0

        while found_asset is None and idx < len(assets):
            if assets[idx].theName == asset_name:
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
                envPropertyDict = envPropertiesDict.get(envProperty.theEnvironmentName,
                                                        AssetEnvironmentPropertiesModel(envProperty.theEnvironmentName))
                syProperties = envProperty.properties()
                pRationale = envProperty.rationale()
                cProperty = syProperties[armid.C_PROPERTY]
                cRationale = pRationale[armid.C_PROPERTY]
                if cProperty != armid.NONE_VALUE:
                    prop_name = 'Confidentiality'
                    attr = AssetSecurityAttribute(armid.C_PROPERTY, prop_name, values[cProperty], cRationale)
                    envPropertyDict.attributesDictionary[prop_name] = attr

                iProperty = syProperties[armid.I_PROPERTY]
                iRationale = pRationale[armid.I_PROPERTY]
                if iProperty != armid.NONE_VALUE:
                    prop_name = 'Integrity'
                    attr = AssetSecurityAttribute(armid.I_PROPERTY, prop_name, values[iProperty], iRationale)
                    envPropertyDict.attributesDictionary[prop_name] = attr

                avProperty = syProperties[armid.AV_PROPERTY]
                avRationale = pRationale[armid.AV_PROPERTY]
                if avProperty != armid.NONE_VALUE:
                    prop_name = 'Availability'
                    attr = AssetSecurityAttribute(armid.AV_PROPERTY, prop_name, values[avProperty], avRationale)
                    envPropertyDict.attributesDictionary[prop_name] = attr

                acProperty = syProperties[armid.AC_PROPERTY]
                acRationale = pRationale[armid.AC_PROPERTY]
                if acProperty != armid.NONE_VALUE:
                    prop_name = 'Accountability'
                    attr = AssetSecurityAttribute(armid.AC_PROPERTY, prop_name, values[acProperty], acRationale)
                    envPropertyDict.attributesDictionary[prop_name] = attr

                anProperty = syProperties[armid.AN_PROPERTY]
                anRationale = pRationale[armid.AN_PROPERTY]
                if anProperty != armid.NONE_VALUE:
                    prop_name = 'Anonymity'
                    attr = AssetSecurityAttribute(armid.AN_PROPERTY, prop_name, values[anProperty], anRationale)
                    envPropertyDict.attributesDictionary[prop_name] = attr

                panProperty = syProperties[armid.PAN_PROPERTY]
                panRationale = pRationale[armid.PAN_PROPERTY]
                if panProperty != armid.NONE_VALUE:
                    prop_name = 'Pseudonymity'
                    attr = AssetSecurityAttribute(armid.PAN_PROPERTY, prop_name, values[panProperty], panRationale)
                    envPropertyDict.attributesDictionary[prop_name] = attr

                unlProperty = syProperties[armid.UNL_PROPERTY]
                unlRationale = pRationale[armid.UNL_PROPERTY]
                if unlProperty != armid.NONE_VALUE:
                    prop_name = 'Unlinkability'
                    attr = AssetSecurityAttribute(armid.UNL_PROPERTY, prop_name, values[unlProperty], unlRationale)
                    envPropertyDict.attributesDictionary[prop_name] = attr

                unoProperty = syProperties[armid.UNO_PROPERTY]
                unoRationale = pRationale[armid.UNO_PROPERTY]
                if unoProperty != armid.NONE_VALUE:
                    prop_name = 'Unobservability'
                    attr = AssetSecurityAttribute(armid.UNO_PROPERTY, prop_name, values[unoProperty], unoRationale)
                    envPropertyDict.attributesDictionary[prop_name] = attr

                if envProperty.theAssociations is not None:
                    envPropertyDict.associations = envProperty.theAssociations

                envPropertyDict.json_prepare()
                envPropertiesDict[envProperty.theEnvironmentName] = envPropertyDict

            resp = make_response(json_serialize(envPropertiesDict.values(), session_id=session_id))
            resp.contenttype = 'application/json'
            return resp

    # region Swagger Doc
    @swagger.operation(
        notes='Updates the environment properties for a specific asset',
        nickname='asset-envprops-by-name-put',
        responseClass=str.__name__,
        parameters=[
            {
                "name": "body",
                "required": True,
                "allowMultiple": False,
                "dataType": AssetEnvironmentPropertiesModel.__name__,
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
        session_id = request.args.get('session_id', None)
        new_json_props = request.get_json(silent=True)

        if new_json_props is False or not isinstance(new_json_props, dict):

            raise MalformedJSONHTTPError()

        session_id = new_json_props.get('session_id', session_id)
        new_env_props = json_deserialize(new_json_props['object'])
        db_proxy = validate_proxy(session, session_id)

        assets = db_proxy.getAssets()
        if len(assets) > 0:
            assets = assets.values()
        else:
            raise CairisHTTPError(
                status_code=httplib.NOT_FOUND,
                message='There were no Assets found in the database.',
                status='No assets found'
            )

        found_asset = None
        idx = 0

        while found_asset is None and idx < len(assets):
            if assets[idx].theName == asset_name:
                found_asset = assets[idx]
            idx += 1

        if not isinstance(found_asset, Asset):
            raise CairisHTTPError(status_code=httplib.CONFLICT,
                                  message='There is no asset in the database with the specified ID',
                                  status='Asset not found')

        if found_asset is None:
            raise CairisHTTPError(
                status_code=httplib.CONFLICT,
                message='There is no asset in the database with the specified ID',
                status='Asset not found'
            )
        else:
            values = ['None', 'Low', 'Medium', 'High']
            envProperties = []
            class_def = AssetEnvironmentPropertiesModel.__module__ + '.' + AssetEnvironmentPropertiesModel.__name__
            assert isinstance(new_env_props, collections.Iterable)

            for new_env_prop in new_env_props:
                obj_def = new_env_prop.__class__.__module__ + '.' + new_env_prop.__class__.__name__
                if class_def != obj_def:
                    raise MalformedJSONHTTPError()
                env_name = new_env_prop.environment

                # Associations should be a list of tuples
                associations = list()
                for idx in range(0, len(new_env_prop.associations)):
                    associations.append(tuple(new_env_prop.associations[idx]))

                # Security attributes are represented by properties and rationales
                properties = array((0, 0, 0, 0, 0, 0, 0, 0)).astype(numpy.int32)
                rationales = 8 * ['None']
                for attribute in new_env_prop.attributes:
                    assert isinstance(attribute, AssetSecurityAttribute)
                    if attribute.id < 0 or attribute.id > 7:
                        msg = 'Invalid attribute index (index={0}). Attribute is being ignored.'.format(attribute.id)
                        raise SilentHTTPError(message=msg)
                    value = attribute.get_attr_value(values)
                    properties[attribute.id] = value
                    rationales[attribute.id] = attribute.rationale

                env_prop = AssetEnvironmentProperties(env_name, properties, rationales, associations)
                envProperties.append(env_prop)

            found_asset.theEnvironmentProperties = envProperties
            params = AssetParameters(
                found_asset.theName,
                found_asset.theShortCode,
                found_asset.theDescription,
                found_asset.theSignificance,
                found_asset.theType,
                found_asset.isCritical,
                found_asset.theCriticalRationale,
                found_asset.theTags,
                found_asset.theInterfaces,
                envProperties
            )
            params.setId(found_asset.theId)
            db_proxy.updateAsset(params)

            resp = make_response('The asset properties were successfully updated.', httplib.OK)
            resp.contenttype = 'application/json'
            return resp