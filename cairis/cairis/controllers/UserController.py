import cherrypy
from json import loads, dumps
from jsonpickle import encode as json_serialize
from jsonpickle import decode as json_deserialize
from Borg import Borg
from CairisHTTPError import CairisHTTPError
from SessionValidator import validate_proxy
from urllib2 import quote


__author__ = 'Robin Quetin'


class UserController(object):
    def set_db(self, conf=None, host=None, port=None, user=None, passwd=None, db=None):
        if cherrypy.request.method == 'POST':
            if conf is not None:
                dbconf = json_deserialize(conf)
                msg = self.set_dbproxy(dbconf)
                code = 200
                status = 'OK'
                return json_serialize({'message': msg, 'code': code, 'status': status})
            elif host is not None and port is not None and user is not None and passwd is not None and db is not None:
                conf = {
                    'host': host,
                    'port': int(port),
                    'user': user,
                    'passwd': passwd,
                    'db': db
                }
                result = self.set_dbproxy(conf)
                conf['fontName'] = cherrypy.session['fontName']
                conf['fontSize'] = cherrypy.session['fontSize']
                conf['apFontSize'] = cherrypy.session['apFontSize']

                cherrypy.response.headers['Content-Type'] = 'text/plain'
                return '{0}\nSession vars:\n{1}\nQuery string:\n{2}'.format(
                    result,
                    dumps(loads(json_serialize(conf)), indent=4),
                    quote(json_serialize(conf))
                )
                return result
            else:
                CairisHTTPError(msg='One or more settings are missing')
        elif cherrypy.request.method == 'GET':
            b = Borg()
            return b.template_generator.serve_result('user_config', action_url=cherrypy.request.path_info)

    def set_dbproxy(self, conf):
        db_proxy = validate_proxy(None, conf)
        pSettings = db_proxy.getProjectSettings()

        cherrypy.session['dbProxy'] = db_proxy
        cherrypy.session['fontSize'] = pSettings['Font Size']
        cherrypy.session['apFontSize'] = pSettings['AP Font Size']
        cherrypy.session['fontName'] = pSettings['Font Name']

        return 'Configuration successfully applied'