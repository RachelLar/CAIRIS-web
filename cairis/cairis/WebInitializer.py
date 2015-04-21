import os
import cherrypy
from Borg import Borg
from controllers.AssetController import AssetController
from controllers.EnvironmentController import EnvironmentController
from controllers.ExceptionController import ExceptionController
from controllers.IndexController import IndexController
from controllers.RequirementController import RequirementController
from controllers.UserController import UserController

__author__ = 'Robin Quetin'
''' This module uses CherryPy (tested using 3.6.0) & Routes (tested using 1.13) '''


def start():
    b = Borg()

    asset_controller = AssetController()
    environment_controller = EnvironmentController()
    exception_controller = ExceptionController()
    index_controller = IndexController()
    requirement_controller = RequirementController()
    user_controller = UserController()

    dispatcher = cherrypy.dispatch.RoutesDispatcher()

    # Asset routes
    dispatcher.connect('assets-all', '/assets/all', asset_controller.all)
    dispatcher.connect('asset-by-name', '/assets/name/{name}', asset_controller.get_asset)
    dispatcher.connect('asset-view-model', '/assets/view', asset_controller.view_asset_model)

    # Index route
    dispatcher.connect('index', '/', index_controller.index)

    # Environment routes
    dispatcher.connect('environments-all', '/environments/all', environment_controller.all)
    dispatcher.connect('environments-all-names', '/environments/all/names', environment_controller.all_names)

    # Exception route
    dispatcher.connect('exception', '/exception', exception_controller.handle_exception)

    # Requirement routes
    dispatcher.connect('requirements-all', '/requirements/all', requirement_controller.all)
    dispatcher.connect('requirement-by-id', '/requirements/{id}', requirement_controller.get_requirement)

    # User routes
    dispatcher.connect('config', '/user/config', user_controller.set_db)

    # For development
    b.staticDir = '/home/student/Documents/CAIRIS-web/cairis/cairis/public'

    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.sessions.storage_type': 'ram',
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
        '/index.html': {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': os.path.join(b.staticDir, 'index.html')
        },
    }

    cherrypy.config.update({
        'server.socket_port': b.webPort,
        'server.socket_host': '0.0.0.0'
    })
    cherrypy.tree.mount(None, "/", config=conf)
    cherrypy.quickstart(None, config=conf)
