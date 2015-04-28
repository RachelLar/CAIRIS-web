import os
import WebConfig
from Borg import Borg
from flask import Flask, session
from flask.ext.cors import CORS
from flask.ext.restful import Api
from flask.ext.restful_swagger import swagger
from controllers import AssetController, CImportController, DimensionController, EnvironmentController, RequirementController

__author__ = 'Robin Quetin'
''' This module uses CherryPy (tested using 3.6.0) & Routes (tested using 1.13) '''


app = Flask(__name__)
api = swagger.docs(Api(app), apiVersion='0.1', description='CAIRIS API', api_spec_url='/api/cairis')
cors = CORS(app)

def start(settings):
    WebConfig.config(settings)
    b = Borg()

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
    api.add_resource(RequirementController.FilteredRequirementsAPI, '/api/requirements/filter/{filter}')
    api.add_resource(RequirementController.RequirementByIdAPI, '/api/requirements/id/{id}')
    api.add_resource(RequirementController.RequirementUpdateAPI, '/api/requirements/update')

    # User routes
    # dispatcher.connect('config', '/user/config', user_controller.set_db)

    # For development
    #b.staticDir = '/home/student/Documents/CAIRIS-web/cairis/cairis/static'

    # set the secret key.  keep this really secret:
    app.secret_key = os.urandom(24)

    app.run(debug=True, host='0.0.0.0', port=b.webPort)