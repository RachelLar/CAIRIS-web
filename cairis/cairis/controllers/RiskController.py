import httplib
from flask import session, request, make_response
from flask.ext.restful import Resource
from flask.ext.restful_swagger import swagger
from tools.JsonConverter import json_serialize
from tools.ModelDefinitions import RiskModel as SwaggerRiskModel
from tools.SessionValidator import validate_proxy

__author__ = 'Robin Quetin'


class RisksAPI(Resource):
    #region Swagger Doc
    @swagger.operation(
        notes='Get all risks',
        responseClass=SwaggerRiskModel.__name__,
        nickname='risks-get',
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
                "description": "An ID used to filter the risks",
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
    #endregion
    def get(self):
        session_id = request.args.get('session_id', None)
        db_proxy = validate_proxy(session, session_id)
        constraint_id = request.args.get('constraint_id', -1)

        risks = db_proxy.getRisks(constraint_id)

        resp = make_response(json_serialize(risks, session_id=session_id), 200)
        resp.contenttype = 'application/json'
        return resp