import os

from flask import Flask
from flask.ext.cors import CORS
from flask.ext.restful import Api
from flask.ext.restful_swagger import swagger

from controllers.AssetController import AssetsAPI, AssetModelAPI
from controllers.CImportController import CImportAPI
from controllers.DimensionController import DimensionsAPI, DimensionNamesAPI
from controllers.EnvironmentController import EnvironmentsAPI, EnvironmentNamesAPI


__author__ = 'Robin Quetin'
''' This module uses CherryPy (tested using 3.6.0) & Routes (tested using 1.13) '''

def start():
    app = Flask(__name__)
    api = swagger.docs(Api(app), apiVersion='0.1', description='CAIRIS API', api_spec_url='/api/cairis')
    cors = CORS(app)

    # Asset routes
    api.add_resource(AssetsAPI, '/api/assets/all/names')
    api.add_resource(AssetModelAPI, '/api/assets/view')

    # CImport
    api.add_resource(CImportAPI, '/api/cimport')

    # DimensionController
    api.add_resource(DimensionsAPI, '/api/dimensions/table/<table>')
    api.add_resource(DimensionNamesAPI, '/api/dimensions/table/<table>/environment/<environment>')

    # Index route
    # dispatcher.connect('index', '/', index_controller.index)

    # Environment routes
    api.add_resource(EnvironmentsAPI, '/api/environments')
    api.add_resource(EnvironmentNamesAPI, '/api/environments/names')

    # Exception route
    # dispatcher.connect('exception', '/exception', exception_controller.handle_exception)

    # Requirement routes
    # dispatcher.connect('requirements-all', '/api/requirements/all', requirement_controller.all)
    # dispatcher.connect('requirements-filtered', '/api/requirements/filter/{filter}', requirement_controller.get_filtered_requirements)
    # dispatcher.connect('requirement-by-id', '/api/requirements/id/{id}', requirement_controller.get_requirement_by_id)
    # dispatcher.connect('requirement-update', '/api/requirements/update', requirement_controller.update_requirement)

    # User routes
    # dispatcher.connect('config', '/user/config', user_controller.set_db)

    # For development
    #b.staticDir = '/home/student/Documents/CAIRIS-web/cairis/cairis/public'

    # set the secret key.  keep this really secret:
    app.secret_key = os.urandom(24)

    app.run(debug=True)