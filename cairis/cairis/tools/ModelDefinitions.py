from flask.ext.restful import fields
from flask.ext.restful_swagger import swagger

__author__ = 'Robin Quetin'


@swagger.model
class CImportParams(object):
    resource_fields = {
        'file_contents': fields.String,
        'type': fields.String,
        'overwrite': fields.Integer
    }
    required=['file_contents', 'type']