import json
import cherrypy
from Borg import Borg
from MySQLDatabaseProxy import MySQLDatabaseProxy

__author__ = 'student'

class UserController(object):
    @cherrypy.expose
    def login(self):
        b = Borg()
        b.logger.info('Method: '+cherrypy.request.method)

        if cherrypy.request.method == 'POST':
            cherrypy.session['IsLoggedIn'] = 1
            return 'It works! You should be logged in now!'
        elif cherrypy.request.method == 'GET':
            cherrypy.response.headers['Content-Type'] = 'text/html'
            return b.template_generator.serve_result('login_get', action_url=cherrypy.request.path_info)
        else:
            return 'Error'

    def logout(self):
        cherrypy.session.clear()
        return "It worked! You should be logged out now!"

    def setdb(self, conf=None, host=None, port=None, user=None, passwd=None, db=None):
        if cherrypy.request.method == 'POST':
            if conf is not None:
                dbconf = json.loads(conf)
                return self.setdbproxy(host=dbconf['host'], port=int(dbconf['port']), user=dbconf['user'], passwd=dbconf['passwd'], db=dbconf['db'])
            elif host is not None and port is not None and user is not None and passwd is not None and db is not None:
                return self.setdbproxy(host, int(port), user, passwd, db)
        elif cherrypy.request.method == 'GET':
            b = Borg()
            return b.template_generator.serve_result('setdb', action_url=cherrypy.request.path_info)

    def test_json(self):
        dbProxy = {
            'host': 'localhost',
            'port': 3306,
            'user': 'cairis',
            'passwd': 'cairis123',
            'db': 'cairis'
        }
        return json.dumps(dbProxy)

    def setdbproxy(self, host, port, user, passwd, db):
        dbProxy = MySQLDatabaseProxy(host=host, port=port, user=user, passwd=passwd, db=db)
        if dbProxy is not None:
            cherrypy.session['dbProxy'] = dbProxy
            cherrypy.response.status = 200
            return 'Configuration successfully applied'
        else:
            cherrypy.response.status = 400
            return 'Failed to configure the database connection'