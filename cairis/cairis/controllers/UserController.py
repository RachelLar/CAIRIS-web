import httplib

from flask.ext.restful_swagger import swagger
from flask import request, make_response, session
from flask.ext.restful import Resource
from jsonpickle import encode

from Borg import Borg
from CairisHTTPError import MissingParameterHTTPError, MalformedJSONHTTPError
from tools.ModelDefinitions import UserConfigModel
from tools.SessionValidator import validate_proxy, get_logger

__author__ = 'Robin Quetin'


def set_dbproxy(conf):
    b = Borg()
    db_proxy = validate_proxy(None, -1, conf=conf)
    pSettings = db_proxy.getProjectSettings()

    id = b.init_settings()
    db_proxy.close()
    session['session_id'] = id
    b.settings[id]['dbProxy'] = db_proxy
    b.settings[id]['dbUser'] = conf['user']
    b.settings[id]['dbPasswd'] = conf['passwd']
    b.settings[id]['dbHost'] = conf['host']
    b.settings[id]['dbPort'] = conf['port']
    b.settings[id]['dbName'] = conf['db']
    b.settings[id]['fontSize'] = pSettings['Font Size']
    b.settings[id]['apFontSize'] = pSettings['AP Font Size']
    b.settings[id]['fontName'] = pSettings['Font Name']
    b.settings[id]['jsonPrettyPrint'] = conf.get('jsonPrettyPrint', False)

    return b.settings[id]


class UserConfigAPI(Resource):
    # region Swagger Doc
    @swagger.operation(
        notes='Sets up the user session',
        nickname='user-config-post',
        responseClass=str.__name__,
        parameters=[
            {
                'name': 'body',
                "description": "The configuration settings for the user's session",
                "required": True,
                "allowMultiple": False,
                'type': UserConfigModel.__name__,
                'paramType': 'body'
            }
        ],
        responseMessages=[
            {
                'code': httplib.BAD_REQUEST,
                'message': 'The method is not callable without setting up a database connection'
            },
            {
                'code': httplib.BAD_REQUEST,
                'message': 'The provided parameters are invalid'
            }
        ]
    )
    # endregion
    def post(self):
        try:
            dict_form = request.get_json(silent=True)

            if dict_form is False or dict_form is None:
                raise MalformedJSONHTTPError(data=request.get_data())

            logger = get_logger()
            logger.info(dict_form)
            s = set_dbproxy(dict_form)

            resp_dict = {'session_id': s['session_id'], 'message': 'Configuration successfully applied'}
            resp = make_response(encode(resp_dict), httplib.OK)
            resp.headers['Content-type'] = 'application/json'
            return resp

        except KeyError:
            return MissingParameterHTTPError()