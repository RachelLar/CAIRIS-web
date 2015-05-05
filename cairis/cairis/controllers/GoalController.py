import ARM
import httplib
from Borg import Borg
from CairisHTTPError import CairisHTTPError
from flask import session, request, make_response
from flask.ext.restful_swagger import swagger
from flask_restful import Resource
from GoalParameters import GoalParameters
from KaosModel import KaosModel
from controllers import EnvironmentController
from tools.JsonConverter import json_serialize, json_deserialize
from tools.ModelDefinitions import GoalModel as SwaggerGoalModel
from tools.SessionValidator import validate_proxy, validate_fonts

__author__ = 'Robin Quetin'


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

    #region Swagger Doc
    @swagger.operation(
        notes='Creates a new goal',
        nickname='goal-post',
        parameters=[
            {
                "name": "body",
                "description": "The serialized version of the new goal to be added",
                "required": True,
                "allowMultiple": False,
                "type": SwaggerGoalModel.__name__,
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
        new_json_goal = request.get_json(silent=True)
        if new_json_goal is False:
            raise CairisHTTPError(httplib.BAD_REQUEST,
                                  'The request body could not be converted to a JSON object.' +
                                  '''Check if the request content type is 'application/json' ''' +
                                  'and that the JSON string is well-formed',
                                  'Unreadable JSON data')

        goal = json_deserialize(new_json_goal, 'goal')

        try:
            db_proxy.nameCheck(goal.theName, 'goal')
        except ARM.ARMException, errorText:
            raise CairisHTTPError(httplib.CONFLICT, errorText.value, 'Database conflict')

        goalParams = GoalParameters(goal.theName, goal.originator(). goal.tags(), goal.environmentProperties())

        try:
            resp_dict = dict()
            resp_dict['goal_id'] = db_proxy.addGoal(goalParams)
            resp = make_response(json_serialize(resp_dict), 200)
            resp.contenttype = 'application/json'
            return resp
        except ARM.ARMException, ex:
            raise CairisHTTPError(httplib.CONFLICT, ex.value, 'Database conflict')

class ColouredGoalsAPI(Resource):
    #region Swagger Doc
    @swagger.operation(
        notes='Get all goals with associated goals',
        responseClass=SwaggerGoalModel.__name__,
        nickname='goals-coloured-get',
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
        goals = db_proxy.getColouredGoals()

        resp = make_response(json_serialize(goals, session_id=session_id))
        resp.headers['Content-Type'] = "application/json"
        return resp

class GoalByIdAPI(Resource):
    # region Swagger Doc
    @swagger.operation(
        notes='Get detailed information about a goal',
        responseClass=SwaggerGoalModel.__name__,
        nickname='goal-by-id-get',
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
        goals = db_proxy.getGoals()

        found_goal = None
        idx = 0
        while found_goal is None and idx < len(goals):
            if goals.values()[idx].theId == id:
                found_goal = goals.values()[idx]
            idx += 1

        resp = make_response(json_serialize(found_goal, session_id=session_id))
        resp.headers['Content-Type'] = "application/json"
        return resp

    #region Swagger Doc
    @swagger.operation(
        notes='Updates an existing goal',
        nickname='goal-put',
        parameters=[
            {
                "name": "body",
                "description": "The serialized version of the goal to be updated",
                "required": True,
                "allowMultiple": False,
                "type": SwaggerGoalModel.__name__,
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
    def put(self, id):
        session_id = request.args.get('session_id', None)
        db_proxy = validate_proxy(session, session_id)
        new_json_goal = request.get_json(silent=True)
        if new_json_goal is False:
            raise CairisHTTPError(status_code=httplib.BAD_REQUEST,
                                  message='The request body could not be converted to a JSON object.' +
                                          '''Check if the request content type is 'application/json' ''' +
                                          'and that the JSON string is well-formed',
                                  status='Unreadable JSON data')

        goal = json_deserialize(new_json_goal, 'goal')

        try:
            db_proxy.nameCheck(goal.theName, 'goal')
        except ARM.ARMException, errorText:
            if str(errorText.value).find(' already exists') < 0:
                raise CairisHTTPError(
                    status_code=httplib.NOT_FOUND,
                    message='The goal does not exist in the database and can therefore not be updated',
                    status='Goal not found')

        goalParams = GoalParameters(goal.theName, goal.originator(). goal.tags(), goal.environmentProperties())

        try:
            resp_dict = dict()
            resp_dict['goal_id'] = db_proxy.updateGoal(goalParams, id=id)
            resp = make_response(json_serialize(resp_dict), 200)
            resp.contenttype = 'application/json'
            return resp
        except ARM.ARMException, ex:
            raise CairisHTTPError(httplib.CONFLICT, ex.value, 'Database conflict')

class GoalByNameAPI(Resource):
    # region Swagger Doc
    @swagger.operation(
        notes='Get detailed information about a goal',
        responseClass=SwaggerGoalModel.__name__,
        nickname='goal-by-name-get',
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
        goals = db_proxy.getGoals()

        found_goal = None
        if goals is not None:
            found_goal = goals.get(name, None)

        resp = make_response(json_serialize(found_goal, session_id=session_id))
        resp.headers['Content-Type'] = "application/json"
        return resp

class GoalModelAPI(Resource):
    # region Swagger Doc
    @swagger.operation(
        notes='Get the goal model for a specific environment',
        responseClass=SwaggerGoalModel.__name__,
        nickname='goal-by-name-get',
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
            },
            {
                "code": 404,
                "message": "Environment not found"
            },
            {
                "code": 405,
                "message": "Environment not defined"
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
                status_code=httplib.BAD_REQUEST,
                message='''The 'environment' query parameter was not provided to the API call.''',
                status='Environment not defined')

        EnvironmentController.checkEnvironment(environment, session_id)

        db_proxy = validate_proxy(session, session_id)
        fontName, fontSize, apFontName = validate_fonts(session, session_id)
        try:
            associationDictionary = db_proxy.goalModel(environment)
            associations = KaosModel(associationDictionary.values(), environment, db_proxy=db_proxy, font_name=fontName,
                font_size=fontSize)
            dot_code = associations.graph()
        except ARM.DatabaseProxyException as ex:
            raise CairisHTTPError(
                status_code=httplib.CONFLICT,
                message=ex.value,
                status='Database conflict'
            )

        resp = make_response(model_generator.generate(dot_code), 200)
        accept_header = request.headers.get('Accept', 'image/svg+xml')
        if accept_header.find('text/plain') > -1:
            resp.headers['Content-type'] = 'text/plain'
        else:
            resp.headers['Content-type'] = 'image/svg+xml'

        return resp