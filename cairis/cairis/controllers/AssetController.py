from flask import request, session, make_response
from flask.ext.restful import Resource, abort
from AssetModel import AssetModel
from Borg import Borg
from tools.JsonConverter import json_serialize
from tools.SessionValidator import validate_proxy, validate_fonts
from flask_restful_swagger import swagger

__author__ = 'Robin Quetin'


class AssetsAPI(Resource):
    @swagger.operation(
        notes='Get a list of assets',
        responseClass=str.__name__,
        responseContainer="List",
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
    def get(self):
        session_id = request.args.get('session_id', None)
        db_proxy = validate_proxy(session, session_id)
        assets = db_proxy.getDimensionNames('asset')

        resp = make_response(json_serialize(assets, session_id=session_id))
        resp.headers['Content-Type'] = "application/json"
        return resp

class AssetModelAPI(Resource):
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
    def get(self):
        b = Borg()
        model_generator = b.model_generator

        session_id = request.args.get('session_id', None)
        environment = request.args.get('environment', None)

        if environment is None:
            abort(405, message='Environment not defined')

        db_proxy = validate_proxy(session, session_id)
        fontName, fontSize, apFontName = validate_fonts(session, session_id)
        associationDictionary = db_proxy.classModel(environment)
        associations = AssetModel(associationDictionary.values(), environment, db_proxy=db_proxy, fontName=fontName, fontSize=fontSize)
        dot_code = associations.graph()

        resp = make_response(model_generator.generate(dot_code), 200)
        resp.headers['Content-type'] = 'image/svg+xml'

        return resp