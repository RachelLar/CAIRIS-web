from flask.ext.restful import fields
from flask.ext.restful_swagger import swagger
from Countermeasure import Countermeasure

from EnvironmentParameters import EnvironmentParameters
from RoleEnvironmentProperties import RoleEnvironmentProperties


__author__ = 'Robin Quetin'

@swagger.model
class EnvironmentTensionModel(object):
    resource_fields = {
        "base_attr_id": fields.Integer,
        "attr_id": fields.Integer,
        "value": fields.Integer,
        "rationale": fields.String
    }
    required = resource_fields.keys()

    base_attr_values = range(-1,4)
    attr_values = range(4,8)
    attr_values.append(-1)

    def __init__(self, base_attr_id=-1, attr_id=-1, value=0, rationale='None', key=None):
        """
        :type base_attr_id: int
        :type attr_id: int
        :type value: int|tuple
        :type rationale: str
        :type key: tuple
        """
        if key is not None:
            base_attr_id = key[0]
            attr_id = key[1]
            rationale = value[1]
            value = value[0]

        if base_attr_id not in self.base_attr_values or attr_id not in self.attr_values:
            raise ValueError('Base attribute or subattribute value is incorrect.')

        self.base_attr_id = base_attr_id
        self.attr_id = attr_id
        self.value = value
        self.rationale = rationale

    def to_tension(self):
        return (self.base_attr_id, self.attr_id), (self.value, self.rationale)

@swagger.model
class TensionDictionaryModel(object):
    def __init__(self):
        self._key_ = None

    resource_fields = {
        "_key_": fields.List(fields.Integer),
        "_value_": fields.List(fields.String)
    }

@swagger.model
@swagger.nested(
    theTensions=TensionDictionaryModel.__name__,
    theTensionsList=EnvironmentTensionModel.__name__
)
class EnvironmentModel(object):
    resource_fields = {
        "theId": fields.Integer,
        "theName": fields.String,
        "theShortCode": fields.String,
        "theDescription": fields.String,
        "theEnvironments": fields.List(fields.String),
        "theDuplicateProperty": fields.String,
        "theOverridingEnvironment": fields.String,
        "theTensions": fields.List(fields.Nested(TensionDictionaryModel.resource_fields)),
        "theTensionsList": fields.List(fields.Nested(EnvironmentTensionModel.resource_fields))
    }
    required = resource_fields.keys()
    required.remove("theTensions")

    def __init__(self, id=None, name=None, sc=None, description=None, environments=[], duplProperty='', overridingEnvironment='', envTensions={}, envTensionList=None, origEnv=None):
        """
        :type id: int
        :type name: str
        :type sc: str
        :type description: str
        :type environments: list
        :type duplProperty: str
        :type overridingEnvironment: str
        :type envTensions: list
        :type envTensionList: list
        :type origEnv: Environment
        """
        if origEnv is not None:
            from Environment import Environment
            assert isinstance(origEnv, Environment)
            self.theId = origEnv.theId
            self.theName = origEnv.theName
            self.theShortCode = origEnv.theShortCode
            self.theDescription = origEnv.theDescription
            self.theEnvironments = origEnv.theEnvironments
            self.theDuplicateProperty = origEnv.theDuplicateProperty
            self.theOverridingEnvironment = origEnv.theOverridingEnvironment
            self.theTensions = origEnv.theTensions
            self.theTensionsList = []
        else:
            self.theId = id
            self.theName = name
            self.theShortCode = sc
            self.theDescription = description
            self.theEnvironments = environments
            self.theDuplicateProperty = duplProperty
            self.theOverridingEnvironment = overridingEnvironment
            self.theTensions = envTensions
            self.theTensionsList=[]

        for key in self.theTensions:
            self.theTensionsList.append(EnvironmentTensionModel(key=key, value=self.theTensions[key]))
        self.theTensions = None

    def to_environment_params(self, for_update=False):
        """
        :type for_update: bool
        """
        missing_values = (self.theId is None or
                          self.theName is None or
                          self.theShortCode is None or
                          self.theDescription is None or
                          self.envTensionList is None or
                          len(self.theTensionsList) != 16)

        if not missing_values:
            self.theTensions = {}
            for tensionModel in self.envTensionList:
                assert isinstance(tensionModel, EnvironmentTensionModel)
                key, value = tensionModel.to_tension()
                self.theTensions[key] = value

            assert len(self.theTensions) == 16

            params = EnvironmentParameters(
                conName=self.theName,
                conSc=self.theShortCode,
                conDesc=self.theDescription,
                environments=self.theEnvironments,
                duplProperty=self.theDuplicateProperty,
                overridingEnvironment=self.theOverridingEnvironment,
                envTensions=self.theTensions
            )

            if for_update:
                params.setId(self.theId)

            return params