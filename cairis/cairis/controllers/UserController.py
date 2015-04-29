from flask.ext.restful_swagger import swagger
from CairisHTTPError import CairisHTTPError
from Borg import Borg
from flask import request, make_response, session
from flask.ext.restful import Resource
from tools.ModelDefinitions import UserConfigModel
from tools.SessionValidator import validate_proxy

__author__ = 'Robin Quetin'


def set_dbproxy(conf):
    b = Borg()
    db_proxy = validate_proxy(None, -1, conf)
    pSettings = db_proxy.getProjectSettings()

    id = b.init_settings()
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
    @swagger.operation(
        notes='Sets up the user session',
        nickname='user-config-post',
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
                'code': 400,
                'message': 'The provided file is not a valid XML file'
            },
            {
                'code': 405,
                'message': '''Some parameters are missing.'''
            }
        ]
    )
    def post(self):
        try:
            dict_form = request.get_json()
            s = set_dbproxy(dict_form)

            resp = make_response('session_id={0}'.format(s['session_id']), 200)
            resp.headers['Content-type'] = 'text/plain'
            return resp

        except KeyError:
            return CairisHTTPError(405, message='One or more settings are missing')