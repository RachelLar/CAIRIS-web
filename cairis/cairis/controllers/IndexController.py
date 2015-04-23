import os
import cherrypy
from Borg import Borg

__author__ = 'Robin Quetin'


class IndexController(object):
    def index(self):
        b = Borg()
        try:
            dbProxyConfigured = cherrypy.session.get('session_id', -1)
            b.logger.info('Database configured: {0}'.format(str(dbProxyConfigured != -1)))
            if dbProxyConfigured != -1:
                return open(os.path.join(b.staticDir, 'index.html')).readlines()
            else:
                raise KeyError('Not configured!')
        except KeyError, ex:
            b.logger.info(str(ex.message))
            raise cherrypy.HTTPRedirect('/user/config')
