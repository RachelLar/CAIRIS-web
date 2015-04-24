import os
import cherrypy
from Borg import Borg
from controllers.AssetController import AssetController
from controllers.CImportController import CImportController
from controllers.DimensionController import DimensionController
from controllers.EnvironmentController import EnvironmentController
from controllers.ExceptionController import ExceptionController
from controllers.IndexController import IndexController
from controllers.RequirementController import RequirementController
from controllers.UserController import UserController

__author__ = 'Robin Quetin'
''' This module uses CherryPy (tested using 3.6.0) & Routes (tested using 1.13) '''

def CORS():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"

def start():
    b = Borg()
    cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)

    asset_controller = AssetController()
    cimport_controller = CImportController()
    dimension_controller = DimensionController()
    environment_controller = EnvironmentController()
    exception_controller = ExceptionController()
    index_controller = IndexController()
    requirement_controller = RequirementController()
    user_controller = UserController()

    dispatcher = cherrypy.dispatch.RoutesDispatcher()

    # Asset routes
    dispatcher.connect('assets-all', '/api/assets/all', asset_controller.all)
    dispatcher.connect('asset-view-model', '/api/assets/view', asset_controller.view_asset_model)

    # CImport
    dispatcher.connect('cimport', '/api/cimport', cimport_controller.cimport)

    # DimensionController
    dispatcher.connect('dimensions-all', '/api/dimensions/all', dimension_controller.get_dimensions)
    dispatcher.connect('dimensions-all-names', '/api/dimensions/all/names', dimension_controller.get_dimension_names)

    # Index route
    dispatcher.connect('index', '/', index_controller.index)

    # Environment routes
    dispatcher.connect('environments-all', '/api/environments/all', environment_controller.all)
    dispatcher.connect('environments-all-names', '/api/environments/all/names', environment_controller.all_names)

    # Exception route
    dispatcher.connect('exception', '/exception', exception_controller.handle_exception)

    # Requirement routes
    dispatcher.connect('requirements-all', '/api/requirements/all', requirement_controller.all)
    dispatcher.connect('requirements-filtered', '/api/requirements/all/filter/{filter}', requirement_controller.get_filtered_requirements)
    dispatcher.connect('requirement-by-id', '/api/requirements/id/{id}', requirement_controller.get_requirement_by_id)
    dispatcher.connect('requirement-update', '/api/requirements/update', requirement_controller.update_requirement)

    # User routes
    dispatcher.connect('config', '/user/config', user_controller.set_db)

    # For development
    #b.staticDir = '/home/student/Documents/CAIRIS-web/cairis/cairis/public'

    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.sessions.storage_type': 'ram',
            'tools.CORS.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/html'),
                                               ('Cache-Control', 'no-cache, no-store, must-revalidate'),
                                               ('Pragma', 'no-cache'),
                                               ('Expires', 0)],
            'tools.staticdir.root': b.staticDir,
            'request.dispatch': dispatcher
        },
        '/bootstrap': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'bootstrap'
        },
        '/build': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'build'
        },
        '/dist': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'dist'
        },
        '/plugins': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'plugins'
        },
    }

    cherrypy.config.update({
        'server.socket_port': b.webPort,
        'server.socket_host': '0.0.0.0',
    })
    cherrypy.tree.mount(None, "/", config=conf)
    cherrypy.quickstart(None, config=conf)
