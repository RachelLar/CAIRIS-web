import cherrypy
from Borg import Borg
from CairisHTTPError import CairisHTTPError
from SessionValidator import validate_proxy
from tools.JsonConverter import json_serialize
from tools.JsonConverter import json_deserialize


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
                cherrypy.response.headers['Content-Type'] = 'text/plain'

                debug = ''
                debug += '{0}\nSession vars:\n{1}\nQuery string:\n'.format(
                    'Configuration successfully updated',
                    json_serialize(result, pretty_printing=True))
                return debug+'session_id={0}'.format(result['session_id'])
            else:
                CairisHTTPError(msg='One or more settings are missing')
        elif cherrypy.request.method == 'GET':
            b = Borg()
            return b.template_generator.serve_result('user_config', action_url=cherrypy.request.path_info)

    def set_dbproxy(self, conf):
        b = Borg()
        db_proxy = validate_proxy(None, -1, conf)
        pSettings = db_proxy.getProjectSettings()

        id = b.init_settings()
        cherrypy.session['session_id'] = id
        b.settings[id]['dbProxy'] = db_proxy
        b.settings[id]['dbUser'] = conf['user']
        b.settings[id]['dbPasswd'] = conf['passwd']
        b.settings[id]['dbHost'] = conf['host']
        b.settings[id]['dbPort'] = conf['port']
        b.settings[id]['dbName'] = conf['db']
        b.settings[id]['fontSize'] = pSettings['Font Size']
        b.settings[id]['apFontSize'] = pSettings['AP Font Size']
        b.settings[id]['fontName'] = pSettings['Font Name']

        return b.settings[id]