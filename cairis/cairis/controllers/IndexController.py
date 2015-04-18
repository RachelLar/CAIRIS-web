import cherrypy
from Borg import Borg

__author__ = 'Robin Quetin'


class IndexController(object):
    @cherrypy.expose
    def index(self):
        b = Borg()
        try:
            isLoggedIn = cherrypy.session.get('IsLoggedIn', 0)
            b.logger.info('IsLoggedIn: '+str(isLoggedIn))
            if isLoggedIn == 1:
                return "It works!"
            else:
                raise KeyError('Not logged in!')
        except KeyError, ex:
            b.logger.info(str(ex.message))
            raise cherrypy.HTTPRedirect('/user/login')
