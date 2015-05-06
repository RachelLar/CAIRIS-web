import httplib
from flask import session
from jsonpickle import encode as serialize
from jsonpickle import decode as deserialize
from json import dumps, loads
from Asset import Asset
from Borg import Borg
from Goal import Goal
from Requirement import Requirement

__author__ = 'Robin Quetin'


def json_serialize(obj, pretty_printing=False, session_id=None):
    """
    Serializes the Python object to a JSON serialized string.
    :param obj: The object to be serialized
    :type obj: object
    :param pretty_printing: Defines if the string needs to be pretty printed
    :type pretty_printing: bool
    :param session_id: The user's session ID
    :type session_id: int
    :return: Returns a JSON serialized string of the object
    """
    b = Borg()
    if session_id is None:
        session_id = session.get('session_id', None)

    s = b.get_settings(session_id)
    if s is not None:
        pretty_printing = s.get('jsonPrettyPrint', False)

    if pretty_printing:
        return dumps(loads(serialize(obj)), indent=4)
    else:
        return serialize(obj)

def json_deserialize(string, class_name=None):
    """
    Deserializes the JSON object to the appropriate class instance.
    :param string: The JSON string
    :type string: str
    :param class_name: The name of the target class
    :type class_name: str
    :return: Returns a dictionary or a class instance depending on the target class chosen
    :rtype: dict|Asset|Requirement
    """
    dict = deserialize(string)
    if class_name == 'asset':
        return deserialize_asset(dict)
    elif class_name == 'goal':
        return deserialize_goal(dict)
    elif class_name == 'requirement':
        return deserialize_requirement(dict)
    else:
        return dict

def deserialize_asset(dict):
    asset = Asset(
        dict['theId'],
        dict['theName'],
        dict['theShortCode'],
        dict['theDescription'],
        dict['theSignificance'],
        dict['theType'],
        dict['isCritical'],
        dict['theCriticalRationale'],
        dict['theTags'],
        dict['theInterfaces'],
        dict['theEnvironmentProperties']
    )
    return asset

def deserialize_goal(dict):
    goal = Goal(dict['theId'], dict['theName'], dict['theOriginator'], dict['theTags'], dict['theEnvironmentProperties'])
    return goal

def deserialize_requirement(dict):
    req = Requirement(id=dict['theId'], label=dict['theLabel'])
    req.theDescription = dict['theDescription']
    req.theName = dict['theName']
    req.thePriority = dict['thePriority']
    req.theVersion = dict['theVersion']
    req.attrs = dict['attrs']
    req.dirtyAttrs = set(dict['dirtyAttrs'])
    return req