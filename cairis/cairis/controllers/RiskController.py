import httplib
from flask import session, request, make_response
from flask.ext.restful import Resource
from flask.ext.restful_swagger import swagger
from CairisHTTPError import MalformedJSONHTTPError
from tools.JsonConverter import json_serialize, json_deserialize
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
        return resp

    def post(self):
        session_id = request.args.get('session_id', None)
        new_json_message = request.get_json(silent=True)

        if new_json_message is False or new_json_message is None:
            raise MalformedJSONHTTPError(data=request.get_data())

        session_id = new_json_message.get('session_id', session_id)
        new_json_risk = json_serialize(new_json_message)
        db_proxy = validate_proxy(session, session_id)
        new_risk = json_deserialize(new_json_risk, 'risk')
        #TODO: finish Risk post