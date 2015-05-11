import httplib
from os import close as fd_close
from os import remove as remove_file
from tempfile import mkstemp

from flask import make_response, request, session
from flask.ext.restful import Resource
from flask_restful_swagger import swagger
from ARM import DatabaseProxyException, ARMException
from CairisHTTPError import MalformedJSONHTTPError, CairisHTTPError, ARMHTTPError

import cimport
from tools.ModelDefinitions import CImportParams
from tools.SessionValidator import validate_proxy, check_required_keys


__author__ = 'Robin Quetin'


class CImportAPI(Resource):
    # region Swagger Doc
    @swagger.operation(
        notes='Imports data from an XML file',
        nickname='cimport-post',
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
                'code': httplib.BAD_REQUEST,
                'message': 'The provided file is not a valid XML file'
            },
            {
                'code': httplib.BAD_REQUEST,
                'message': '''Some parameters are missing. Be sure 'file_contents' and 'type' are defined.'''
            }
        ]
    )
    # endregion
    def post(self):
        session_id = request.args.get('session_id', None)
        json_dict = request.get_json(silent=True)

        if json_dict is False:
            raise MalformedJSONHTTPError()

        session_id = json_dict.get('session_id', session_id)
        check_required_keys(json_dict, ('file_contents','type'))
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

            try:
                result = cimport.file_import(abs_path, type, overwrite, session_id=session_id)
            except DatabaseProxyException as ex:
                raise ARMHTTPError(ex)
            except ARMException as ex:
                raise ARMHTTPError(ex)
            except Exception as ex:
                raise CairisHTTPError(
                    status_code=500,
                    message=str(ex.message),
                    status='Unknown error'
                )

            remove_file(abs_path)

            resp = make_response(result, httplib.OK)
            resp.headers['Content-Type'] = 'text/plain'
            return resp
        else:
            raise CairisHTTPError(
                status_code=httplib.BAD_REQUEST,
                message='The provided file is not a valid XML file',
                status='Invalid XML input'
            )
