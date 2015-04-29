import os
from Borg import Borg
from flask import Flask, session, redirect, make_response, request
from flask.ext.cors import CORS
from flask.ext.restful import Api
from flask.ext.restful_swagger import swagger
from CairisHTTPError import CairisHTTPError
from controllers import AssetController, CImportController, DimensionController, EnvironmentController, RequirementController, UserController

__author__ = 'Robin Quetin'
''' This module uses CherryPy (tested using 3.6.0) & Routes (tested using 1.13) '''


app = Flask(__name__)
api = swagger.docs(Api(app), apiVersion='0.1', description='CAIRIS API', api_spec_url='/api/cairis')
cors = CORS(app)
b = Borg()

@app.route('/')
def index():
    if session.has_key('session_id'):
        return b.template_generator.serve_result('index')
    else:
        resp = make_response('Moved temporarily', 302)
        resp.headers['Location'] = '/user/config.html'
        return resp

@app.route('/user/config.html', methods=['GET','POST'])
def user_config_get():
    if request.method == 'GET':
        b = Borg()
        resp = make_response(b.template_generator.serve_result('user_config', action_url=request.full_path), 200)
        resp.headers['Content-type'] = 'text/html'
        return resp
    elif request.method == 'POST':
        try:
            dict_form = request.form
            conf = {
                'host': dict_form['host'],
                'port': int(dict_form['port']),
                'user': dict_form['user'],
                'passwd': dict_form['passwd'],
                'db': dict_form['db'],
                'jsonPrettyPrint': dict_form.get('jsonPrettyPrint', False) == 'on'
            }
            s = UserController.set_dbproxy(conf)
            debug = ''
            '''debug += '{0}\nSession vars:\n{1}\nQuery string:\n'.format(
                'Configuration successfully updated',
                json_serialize(s, session_id=s['session_id']))'''

            resp = make_response(debug + 'session_id={0}'.format(s['session_id']), 200)
            resp.headers['Content-type'] = 'text/plain'
            return resp
        except KeyError:
            return CairisHTTPError(405, message='One or more settings are missing')
    else:
        raise CairisHTTPError(404, message='Not found')

@app.errorhandler(CairisHTTPError)
def handle_error(error):
    accept_header = request.headers.get('Accept', 'application/json')
    if accept_header.find('text/html') > -1:
        resp = make_response(error.handle_exception_html(), error.status_code)
        resp.headers['Content-type'] = 'text/html'
        return resp
    else:
        resp = make_response(error.handle_exception_json(), error.status_code)
        resp.headers['Content-type'] = 'application/json'
        return resp

def start():
    # Asset routes
    api.add_resource(AssetController.AssetsAPI, '/api/assets/all/names')
    api.add_resource(AssetController.AssetModelAPI, '/api/assets/view')

    # CImport
    api.add_resource(CImportController.CImportAPI, '/api/cimport')

    # DimensionController
    api.add_resource(DimensionController.DimensionsAPI, '/api/dimensions/table/<table>')
    api.add_resource(DimensionController.DimensionNamesAPI, '/api/dimensions/table/<table>/environment/<environment>')

    # Index route
    # dispatcher.connect('index', '/', index_controller.index)

    # Environment routes
    api.add_resource(EnvironmentController.EnvironmentsAPI, '/api/environments')
    api.add_resource(EnvironmentController.EnvironmentNamesAPI, '/api/environments/names')

    # Exception route
    # dispatcher.connect('exception', '/exception', exception_controller.handle_exception)

    # Requirement routes
    api.add_resource(RequirementController.RequirementsAPI, '/api/requirements/all')
    api.add_resource(RequirementController.RequirementsByAssetAPI, '/api/requirements/asset/<string:name>')
    api.add_resource(RequirementController.RequirementsByEnvironmentAPI, '/api/requirements/environment/<string:name>')
    api.add_resource(RequirementController.RequirementByIdAPI, '/api/requirements/id/{id}')
    api.add_resource(RequirementController.RequirementUpdateAPI, '/api/requirements/update')

    # User routes
    api.add_resource(UserController.UserConfigAPI, '/api/user/config')

    # For development
    #b.staticDir = '/home/student/Documents/CAIRIS-web/cairis/cairis/static'

    # set the secret key.  keep this really secret:
    print(app.error_handler_spec)
    app.secret_key = os.urandom(24)

    app.run(host='0.0.0.0', port=b.webPort)
    app.run(debug=True, host='0.0.0.0', port=b.webPort)