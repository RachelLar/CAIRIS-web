import cherrypy
from Borg import Borg

__author__ = 'Robin Quetin'


class IndexController(object):
    @cherrypy.expose
    def index(self):
        b = Borg()
        try:
            dbProxyConfigured = cherrypy.session.get('dbProxy', False)
            b.logger.info('Database configured: '+str(dbProxyConfigured))
            if dbProxyConfigured:
                return "It works!"
            else:
                raise KeyError('Not configured!')
        except KeyError, ex:
            b.logger.info(str(ex.message))
            raise cherrypy.HTTPRedirect('/user/config')
