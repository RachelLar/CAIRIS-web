import logging
import cherrypy
import cherrypy.lib.cptools

__author__ = 'Robin Quetin'


class LogoutController(object):
    exposed = True
    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        cherrypy.session['IsLoggedIn'] = 0
        return "It worked! You should be logged out now!"
