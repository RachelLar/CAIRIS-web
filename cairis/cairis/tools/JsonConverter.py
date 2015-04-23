from jsonpickle import encode as serialize
from jsonpickle import decode as deserialize
from json import dumps, loads
from Requirement import Requirement

__author__ = 'TChosenOne'

def json_serialize(obj, pretty_printing=False):
    if pretty_printing:
        dumps(loads(serialize(obj)), indent=4)
    else:
        serialize(obj)

def json_deserialize(string, class_name=None):
    dict = deserialize(string)
    if class_name == 'asset':
        pass
    elif class_name == 'requirement':
        return deserialize_requirement(dict)
    else:
        return dict

def deserialize_requirement(dict):
    reqDict = dict.popitem()[1]
    req = Requirement(id=reqDict['theId'], label=reqDict['theLabel'])
    req.theDescription = reqDict['theDescription']
    req.theName = reqDict['theName']
    req.thePriority = reqDict['thePriority']
    req.theVersion = reqDict['theVersion']
    req.attrs = reqDict['attrs']
    req.dirtyAttrs = set(reqDict['dirtyAttrs'])
    return req