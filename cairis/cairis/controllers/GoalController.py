from flask import session, request, make_response
from flask.ext.restful_swagger import swagger
from flask_restful import Resource
from tools.JsonConverter import json_serialize
from tools.ModelDefinitions import GoalModel as SwaggerGoalModel
from tools.SessionValidator import validate_proxy

__author__ = 'TChosenOne'


class GoalsAPI(Resource):
    #region Swagger Doc
    @swagger.operation(
        notes='Get all goals',
        responseClass=SwaggerGoalModel.__name__,
        nickname='goals-get',
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
        goals = db_proxy.getGoals()

        resp = make_response(json_serialize(goals, session_id=session_id))
        resp.headers['Content-Type'] = "application/json"
        return resp