import httplib

from flask import request, session, make_response
from flask.ext.restful import Resource
from flask_restful_swagger import swagger

import ARM
from CairisHTTPError import MalformedJSONHTTPError, ARMHTTPError, ObjectNotFoundHTTPError
from Role import Role
from RoleParameters import RoleParameters
from tools.JsonConverter import json_serialize, json_deserialize
from tools.MessageDefinitions import RoleMessage
from tools.ModelDefinitions import RoleModel
from tools.SessionValidator import validate_proxy


__author__ = 'Robin Quetin'


class RolesAPI(Resource):
    # region Swagger Doc
    @swagger.operation(
        notes='Get all roles',
        responseClass=RoleModel.__name__,
        nickname='roles-get',
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
                "description": "An ID used to filter the roles",
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
        roles = db_proxy.getRoles(constraint_id)

        for key in roles:
            role = roles[key]
            role.theEnvironmentDictionary = {}
            roles[key] = role

        resp = make_response(json_serialize(roles, session_id=session_id))
        resp.headers['Content-Type'] = "application/json"
        return resp

    # region Swagger Doc
    @swagger.operation(
        notes='Creates a new role',
        nickname='role-post',
        parameters=[
            {
                "name": "body",
                "description": "The serialized version of the new role to be added",
                "required": True,
                "allowMultiple": False,
                "type": RoleMessage.__name__,
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
            raise MalformedJSONHTTPError(data=request.get_data())

        session_id = new_json_message.get('session_id', session_id)
        new_json_role = json_serialize(new_json_message['object'])
        db_proxy = validate_proxy(session, session_id)
        role = json_deserialize(new_json_role)
        assert isinstance(role, Role)

        try:
            db_proxy.nameCheck(role.theName, 'role')
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)

        roleParams = RoleParameters(
            name=role.theName,
            rType=role.theType,
            sCode=role.theShortCode,
            desc=role.theDescription,
            cProperties=[]
        )

        try:
            resp_dict = dict()
            resp_dict['role_id'] = db_proxy.addRole(roleParams)
            resp = make_response(json_serialize(resp_dict), httplib.OK)
            resp.contenttype = 'application/json'
            return resp
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)

class RolesByNameAPI(Resource):
    # region Swagger Doc
    @swagger.operation(
        notes='Get an role by name',
        responseClass=RoleModel.__name__,
        nickname='role-by-name-get',
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
        roles = db_proxy.getRoles()
        found_role = None

        if roles is not None:
            found_role = roles.get(name, None)

        if found_role is None:
            raise ObjectNotFoundHTTPError(obj='The provided role name')

        assert isinstance(found_role, Role)
        found_role.theEnvironmentProperties = []
        found_role.theEnvironmentDictionary = []

        resp = make_response(json_serialize(found_role, session_id=session_id))
        resp.headers['Content-Type'] = "application/json"
        return resp

    # region Swagger Doc
    @swagger.operation(
        notes='Updates an existing role',
        nickname='role-put',
        parameters=[
            {
                "name": "body",
                "description": "The session ID and the serialized version of the role to be updated",
                "required": True,
                "allowMultiple": False,
                "type": RoleMessage.__name__,
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
                'message': 'The provided role name could not be found in the database'
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
        new_json_role = request.get_json(silent=True)

        if new_json_role is False or new_json_role is None:
            raise MalformedJSONHTTPError(data=request.get_data())

        session_id = new_json_role.get('session_id', session_id)
        db_proxy = validate_proxy(session, session_id)
        role = json_deserialize(new_json_role['object'], 'role')

        try:
            db_proxy.nameCheck(name, 'role')
            raise ObjectNotFoundHTTPError('The provided role name')
        except ARM.ARMException as ex:
            if str(ex.value).find(' already exists') < 0:
                raise ARMHTTPError(ex)

        roleParams = RoleParameters(
            name=role.theName,
            rType=role.theType,
            sCode=role.theShortCode,
            desc=role.theDescription,
            cProperties=[]
        )
        roleParams.setId(role.theId)

        try:
            db_proxy.updateRole(roleParams)
            resp = make_response('Update successful', httplib.OK)
            resp.contenttype = 'text/plain'
            return resp
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)

    # region Swagger Doc
    @swagger.operation(
        notes='Deletes an existing role',
        nickname='role-delete',
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
                'message': 'The provided role name could not be found in the database'
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
        roles = db_proxy.getRoles()
        found_role = None

        if roles is not None:
            found_role = roles.get(name, None)

        if found_role is None or not isinstance(found_role, Role):
            raise ObjectNotFoundHTTPError('The provided role name')

        db_proxy.deleteRole(found_role.theId)