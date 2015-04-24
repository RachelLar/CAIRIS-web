import cherrypy
import cimport
from CairisHTTPError import CairisHTTPError
from tempfile import mkstemp
from tools.JsonConverter import json_serialize
from os import close as fd_close
from os import remove as remove_file

__author__ = 'TChosenOne'


class CImportController(object):
    def cimport(self, file_contents, type, overwrite=None, session_id=None):
        if file_contents.startswith('<?xml'):
            fd, abs_path = mkstemp(suffix='xml')
            fs_temp = open(abs_path, 'w')
            fs_temp.write(file_contents)
            fs_temp.close()
            fd_close(fd)
            result = cimport.file_import(abs_path, type, overwrite, session_id=session_id)
            remove_file(abs_path)
            cherrypy.response.headers['Content-Type'] = 'application/json'
            return json_serialize({'msg': result}, session_id=session_id)
        else:
            CairisHTTPError(msg='The provided file is not a valid XML file', session_id=session_id)
