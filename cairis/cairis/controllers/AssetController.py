import cherrypy
from AssetModel import AssetModel
from Borg import Borg
from tools.JsonConverter import json_serialize
from tools.SessionValidator import validate_proxy, validate_fonts


__author__ = 'Robin Quetin'

# noinspection PyMethodMayBeStatic
class AssetController(object):
    def __init__(self):
        b = Borg()
        self.model_generator = b.model_generator

    def all(self, session_id=None):
        db_proxy = validate_proxy(cherrypy.session, session_id)
        assets = db_proxy.getDimensionNames('asset')
        return json_serialize(assets, session_id=session_id)

    def view_asset_model(self, environment, session_id=None):
        db_proxy = validate_proxy(cherrypy.session, session_id)
        fontName, fontSize, apFontName = validate_fonts(cherrypy.session, session_id)
        environmentName = environment
        associationDictionary = db_proxy.classModel(environmentName)
        associations = AssetModel(associationDictionary.values(), environmentName, db_proxy=db_proxy, fontName=fontName, fontSize=fontSize)
        dot_code = associations.graph()
        return self.model_generator.generate(dot_code)