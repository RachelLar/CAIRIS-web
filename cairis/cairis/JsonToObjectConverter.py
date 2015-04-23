from Requirement import Requirement

__author__ = 'TChosenOne'


def convert(dict, class_name):
    if class_name == 'asset':
        pass
    elif class_name == 'requirement':
        return convertToRequirement(dict)
    else:
        raise TypeError('Class name for deserialization was not recognized.')

def convertToRequirement(dict):
    reqDict = dict.popitem()[1]
    req = Requirement(id=reqDict['theId'], label=reqDict['theLabel'])
    req.theDescription = reqDict['theDescription']
    req.theName = reqDict['theName']
    req.thePriority = reqDict['thePriority']
    req.theVersion = reqDict['theVersion']
    req.attrs = reqDict['attrs']
    req.dirtyAttrs = set(reqDict['dirtyAttrs'])
    return req