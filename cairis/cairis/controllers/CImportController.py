import httplib
from tempfile import mkstemp
from os import close as fd_close
from os import remove as remove_file
from flask import make_response, request, session
from flask.ext.restful import abort, Resource
from flask_restful_swagger import swagger
from CairisHTTPError import CairisHTTPError
from tools.ModelDefinitions import CImportParams
from tools.SessionValidator import validate_proxy
import cimport


__author__ = 'Robin Quetin'


class CImportAPI(Resource):
    @swagger.operation(
        notes='Imports data from an XML file',
        nickname='asset-model-get',
        parameters=[
            {
                'name':'body',
                "description": "Options to be passed to the import tool",
                "required": True,
                "allowMultiple": False,
                'type': CImportParams.__name__,
                'paramType': 'body'
            },
            {
                "name": "session_id",
                "description": "The ID of the user's session",
                "required": False,
                "allowMultiple": False,
                "dataType": str.__name__,
                "paramType": "query"
            }
        ],
        responseMessages=[
            {
                'code': 400,
                'message': 'The provided file is not a valid XML file'
            },
            {
                'code': 405,
                'message': '''Some parameters are missing. Be sure 'file_contents' and 'type' are defined.'''
            }
        ]
    )
    def post(self):
        session_id = request.args.get('session_id', None)
        json_dict = request.get_json(silent=True)

        if json_dict is False:
            raise CairisHTTPError(httplib.BAD_REQUEST,
                                  'The request body could not be converted to a JSON object.' +
                                  '''Check if the request content type is 'application/json' ''' +
                                  'and that the JSON string is well-formed',
                                  'Unreadable JSON data')

        if not all(reqKey in json_dict for reqKey in ('file_contents','type')):
            return CairisHTTPError(405, '''Some parameters are missing. Be sure 'file_contents' and 'type' are defined.''')

        validate_proxy(session, session_id)
        file_contents = json_dict['file_contents']
        type = json_dict['type']
        overwrite = json_dict.get('overwrite', None)

        if file_contents.startswith('<?xml'):
            fd, abs_path = mkstemp(suffix='xml')
            fs_temp = open(abs_path, 'w')
            fs_temp.write(file_contents)
            fs_temp.close()
            fd_close(fd)
            result = cimport.file_import(abs_path, type, overwrite, session_id=session_id)
            remove_file(abs_path)

            resp = make_response(result, 200)
            resp.headers['Content-Type'] = 'text/plain'
            return resp
        else:
            raise CairisHTTPError(400, 'The provided file is not a valid XML file')
