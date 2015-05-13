import httplib

from flask import session, request, make_response
from flask.ext.restful import Resource
from flask.ext.restful_swagger import swagger

import ARM
from CairisHTTPError import MalformedJSONHTTPError, ARMHTTPError, ObjectNotFoundHTTPError
from Environment import Environment
from tools.MessageDefinitions import EnvironmentMessage
from tools.PseudoClasses import EnvironmentModel
from tools.SessionValidator import validate_proxy, check_environment
from tools.JsonConverter import json_serialize, json_deserialize


__author__ = 'Robin Quetin'


class EnvironmentsAPI(Resource):
    #region Swagger Docs
    @swagger.operation(
        notes='Get all environments',
        nickname='environments-get',
        responseClass=EnvironmentModel.__name__,
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
    #endregion
    def get(self):
        session_id = request.args.get('session_id', None)
        constraintsId = request.args.get('constraints_id', -1)
        db_proxy = validate_proxy(session, session_id)

        environments = db_proxy.getEnvironments(constraintsId)
        env_models = {}

        for key in environments:
            env_models[key] = EnvironmentModel(origEnv=environments[key])

        resp = make_response(json_serialize(env_models, session_id=session_id), httplib.OK)
        resp.headers['Content-type'] = 'application/json'
        return resp

    #region Swagger Docs
    @swagger.operation(
        notes='Add a new environment',
        nickname='environments-post',
        parameters=[
            {
                "name": "body",
                "description": "The session ID and the serialized version of the asset to be updated",
                "required": True,
                "allowMultiple": False,
                "type": EnvironmentMessage.__name__,
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
            },
            {
                "code": MalformedJSONHTTPError.status_code,
                "message": MalformedJSONHTTPError.status
            },
            {
                "code": ARMHTTPError.status_code,
                "message": ARMHTTPError.status
            }
        ]
    )
    #endregion
    def post(self):
        session_id = request.args.get('session_id', None)
        new_json_environment = request.get_json(silent=False)

        if new_json_environment is False or new_json_environment is None:
            raise MalformedJSONHTTPError(data=request.get_data())

        session_id = new_json_environment.get('session_id', session_id)
        new_environment = json_deserialize(new_json_environment['object'])

        if not isinstance(new_environment, EnvironmentModel):
            raise MalformedJSONHTTPError(data=request.get_data())

        new_environment_params = new_environment.to_environment_params()
        db_proxy = validate_proxy(session, session_id)
        try:
            db_proxy.addEnvironment(new_environment_params)
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)

        resp = make_response('Environment successfully added', httplib.OK)
        resp.headers['Content-type'] = 'application/json'
        return resp

class EnvironmentByNameAPI(Resource):
    #region Swagger Docs
    @swagger.operation(
        notes='Get detailed information about an environment',
        nickname='environment-by-name-get',
        responseClass=EnvironmentModel.__name__,
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
    #endregion
    def get(self, name):
        session_id = request.args.get('session_id', None)
        constraintsId = request.args.get('constraints_id', -1)
        db_proxy = validate_proxy(session, session_id)

        environments = db_proxy.getEnvironments(constraintsId)
        if environments is None:
            raise ObjectNotFoundHTTPError(obj='The specified environment name')

        found_environment = environments.get(name, None)
        if found_environment is None:
            raise ObjectNotFoundHTTPError(obj='The specified environment name')

        assert isinstance(found_environment, Environment)
        found_environment = EnvironmentModel(origEnv = found_environment)

        resp = make_response(json_serialize(found_environment, session_id=session_id), httplib.OK)
        resp.headers['Content-type'] = 'application/json'
        return resp

    # region Swagger Doc
    @swagger.operation(
        notes='Updates an existing environment',
        nickname='environment-name-put',
        parameters=[
            {
                "name": "body",
                "description": "The session ID and the serialized version of the asset to be updated",
                "required": True,
                "allowMultiple": False,
                "type": EnvironmentMessage.__name__,
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
                'code': ObjectNotFoundHTTPError.status_code,
                'message': ObjectNotFoundHTTPError.status
            },
            {
                'code': ARMHTTPError.status_code,
                'message': ARMHTTPError.status
            }
        ]
    )
    # endregion
    def put(self, name):
        session_id = request.args.get('session_id', None)
        new_json_environment = request.get_json(silent=False)

        if new_json_environment is False or new_json_environment is None:
            raise MalformedJSONHTTPError(data=request.get_data())

        session_id = new_json_environment.get('session_id', session_id)
        new_environment = json_deserialize(new_json_environment['object'])

        check_environment(name, session, session_id)

        if not isinstance(new_environment, EnvironmentModel):
            raise MalformedJSONHTTPError(data=request.get_data())

        new_environment_params = new_environment.to_environment_params(for_update=True)
        db_proxy = validate_proxy(session, session_id)
        try:
            db_proxy.updateEnvironment(new_environment_params)
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)

        resp = make_response('Environment successfully updated', httplib.OK)
        resp.headers['Content-type'] = 'application/json'
        return resp

    # region Swagger Doc
    @swagger.operation(
        notes='Delete an existing environment',
        nickname='environment-name-delete',
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
                'code': ObjectNotFoundHTTPError.status_code,
                'message': ObjectNotFoundHTTPError.status
            },
            {
                'code': ARMHTTPError.status_code,
                'message': ARMHTTPError.status
            }
        ]
    )
    # endregion
    def delete(self, name):
        session_id = request.args.get('session_id', None)
        check_environment(name, session, session_id)

        db_proxy = validate_proxy(session, session_id)
        environments = db_proxy.getEnvironments()

        found_environment = None
        if environments is not None:
            found_environment = environments.get(name, None)

        if found_environment is None:
            raise ObjectNotFoundHTTPError(obj='The provided environment name')

        try:
            assert isinstance(found_environment, Environment)
            db_proxy.deleteEnvironment(found_environment.theId)
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)

        resp = make_response('Environment successfully updated', httplib.OK)
        resp.headers['Content-type'] = 'application/json'
        return resp

class EnvironmentNamesAPI(Resource):
    #region Swagger Docs
    @swagger.operation(
        notes='Get all environment names',
        nickname='environment-names-get',
        responseClass=str.__name__,
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
    #endregion
    def get(self):
        session_id = request.args.get('session_id', None)
        db_proxy = validate_proxy(session, session_id)

        environment_names = db_proxy.getEnvironmentNames()
        resp = make_response(json_serialize(environment_names, session_id=session_id), httplib.OK)
        resp.headers['Content-type'] = 'application/json'
        return resp