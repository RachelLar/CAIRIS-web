import cherrypy

from Borg import Borg
from controllers.AssetController import AssetController
from controllers.IndexController import IndexController
from controllers.LoginController import LoginController
from controllers.LogoutController import LogoutController


__author__ = 'Robin Quetin'
''' This module uses CherryPy (tested using 3.6.0) & Routes (tested using 1.13) '''
def start():
    b = Borg()
    indexconf = {
        '/': {
            'tools.sessions.on': True,
            'tools.sessions.storage_type': 'ram',
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/html'),
                                               ('Cache-Control', 'no-cache, no-store, must-revalidate'),
                                               ('Pragma', 'no-cache'),
                                               ('Expires', 0)]
            },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': b.staticDir,
        }
    }

    restconf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.sessions.storage_type': 'ram',
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain'),
                                               ('Cache-Control', 'no-cache, no-store, must-revalidate'),
                                               ('Pragma', 'no-cache'),
                                               ('Expires', 0)],
        }
    }

    cherrypy.config.update({'server.socket_port': b.webPort})
    cherrypy.tree.mount(AssetController(), '/assets/', restconf)
    cherrypy.tree.mount(LoginController(), '/login/', restconf)
    cherrypy.tree.mount(LogoutController(), '/logout/', restconf)
    cherrypy.quickstart(IndexController(), '/', indexconf)
