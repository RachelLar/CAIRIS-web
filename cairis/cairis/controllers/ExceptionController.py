import cherrypy
from Borg import Borg
from json import dumps as json_serialize
from TemplateGenerator import TemplateGenerator

__author__ = 'Robin Quetin'


class ExceptionController(object):
    def __init__(self):
        self.b = Borg()

    def handle_exception(self, msg='', code=404, title='Not Found'):
        cherrypy.response.status = int(code)
        accept_header = cherrypy.request.headers.get('Accept', None)
        if accept_header is not None:
            if accept_header.find('*/*') > -1 or accept_header.find('/html') > -1:

                return self.handle_exception_html(msg, code, title)
            else:
                return self.handle_exception_json(msg, code, title)
        else:
            return self.handle_exception_json(msg, code, title)

    def handle_exception_html(self, msg, code, title):
        self.b.template_generator = TemplateGenerator()
        return self.b.template_generator.serve_result('common.error', msg=msg, code=code, title=title)


    def handle_exception_json(self, msg, code, title):
        return json_serialize({'message': msg, 'code': code, 'status': title})