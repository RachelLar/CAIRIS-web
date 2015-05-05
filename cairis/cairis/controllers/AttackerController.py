from flask import request, session, make_response
from flask.ext.restful import Resource
from flask_restful_swagger import swagger

__author__ = 'Robin Quetin'


class AttackersAPI(Resource):
    #region Swagger Doc
    #endregion
    def get(self):
        return None