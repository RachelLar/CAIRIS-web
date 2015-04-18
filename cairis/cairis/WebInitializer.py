import os
import cherrypy
from Borg import Borg
from controllers.AssetController import AssetController
from controllers.IndexController import IndexController
from controllers.UserController import UserController

__author__ = 'Robin Quetin'
''' This module uses CherryPy (tested using 3.6.0) & Routes (tested using 1.13) '''


def start():
    b = Borg()

    asset_controller = AssetController()
    user_controller = UserController()
    index_controller = IndexController()

    dispatcher = cherrypy.dispatch.RoutesDispatcher()

    # Define the different routes
    dispatcher.connect('assets-all', '/assets/all', asset_controller.all)
    dispatcher.connect('asset-by-name', '/assets/{name}', asset_controller.get_asset)
    dispatcher.connect('db-set', '/user/db/set', user_controller.setdb)
    dispatcher.connect('db-jsontest', '/user/db/jsontest', user_controller.test_json)
    dispatcher.connect('login', '/user/login', user_controller.login)
    dispatcher.connect('logout', '/user/logout', user_controller.logout)
    dispatcher.connect('index', '/', index_controller.index)

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
        '/assets': {},
        '/user': {},
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
        '/index.mako': {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': os.path.join(b.staticDir, 'index.mako')
        },
    }

    cherrypy.config.update({'server.socket_port': b.webPort})
    cherrypy.tree.mount(None, "/", config=conf)
    cherrypy.quickstart(None, config=conf)
