import httplib

from flask import session, make_response
from flask import request
from flask.ext.restful import Resource
from data.UploadDAO import UploadDAO
from tools.JsonConverter import json_serialize

from tools.SessionValidator import get_session_id

__author__ = 'Robin Quetin'


class UploadImageAPI(Resource):
    def post(self):
        session_id = get_session_id(session, request)
        file = request.files['file']

        dao = UploadDAO(session_id)
        filename = dao.upload_image(file)

        resp_dict = {'message': 'File successfully uploaded', 'filename': filename}
        resp = make_response(json_serialize(resp_dict, session_id=session_id), httplib.OK)
        resp.contenttype = 'application/json'
        return resp