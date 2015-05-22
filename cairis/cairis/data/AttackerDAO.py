import ARM
from AttackerEnvironmentProperties import AttackerEnvironmentProperties
from CairisHTTPError import ARMHTTPError, ObjectNotFoundHTTPError, MalformedJSONHTTPError, MissingParameterHTTPError, \
    OverwriteNotAllowedHTTPError
from Attacker import Attacker
from AttackerParameters import AttackerParameters
from data.CairisDAO import CairisDAO
from tools.JsonConverter import json_serialize, json_deserialize
from tools.ModelDefinitions import AttackerModel, AttackerEnvironmentPropertiesModel
from tools.SessionValidator import check_required_keys

__author__ = 'Robin Quetin'


class AttackerDAO(CairisDAO):
    def __init__(self, session_id):
        CairisDAO.__init__(self, session_id)

    def get_attackers(self, constraint_id=-1, simplify=True):
        try:
            attackers = self.db_proxy.getAttackers(constraint_id)
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)

        if simplify:
            for key, value in attackers.items():
                attackers[key] = self.simplify(value)

        return attackers

    def get_attacker_by_name(self, name, constraint_id=-1, simplify=True):
        found_attacker = None
        try:
            attackers = self.db_proxy.getAttackers(constraint_id)
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)

        if attackers is not None:
            found_attacker = attackers.get(name, None)

        if found_attacker is None:
            raise ObjectNotFoundHTTPError('The provided attacker name')

        if simplify:
            found_attacker = self.simplify(found_attacker)

        return found_attacker

    def add_attacker(self, attacker):
        attacker_params = AttackerParameters(
            name=attacker.theName,
            desc=attacker.theDescription,
            image=attacker.theImage,
            tags=attacker.theTags,
            properties=attacker.theEnvironmentProperties
        )

        try:
            if not self.check_existing_attacker(attacker.theName):
                new_id = self.db_proxy.addAttacker(attacker_params)
                return new_id
            else:
                raise OverwriteNotAllowedHTTPError(obj_name=attacker.theName)
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)

    def update_attacker(self, attacker, name):
        found_attacker = self.get_attacker_by_name(name, simplify=False)

        attacker_params = AttackerParameters(
            name=attacker.theName,
            desc=attacker.theDescription,
            image=attacker.theImage,
            tags=attacker.theTags,
            properties=attacker.theEnvironmentProperties
        )
        attacker_params.setId(found_attacker.theId)

        try:
            self.db_proxy.updateAttacker(attacker_params)
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)

    def delete_attacker(self, name):
        found_attacker = self.get_attacker_by_name(name, simplify=False)
        attacker_id = found_attacker.theId

        try:
            self.db_proxy.deleteAttacker(attacker_id)
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)

    def check_existing_attacker(self, name):
        try:
            self.db_proxy.nameCheck(name, 'attacker')
            return False
        except ARM.ARMException as ex:
            if str(ex.value).find('already exists') > -1:
                return True
            raise ARMHTTPError(ex)

    def from_json(self, request):
        json = request.get_json(silent=True)
        if json is False or json is None:
            raise MalformedJSONHTTPError(data=request.get_data())

        json_dict = json['object']
        check_required_keys(json_dict, AttackerModel.required)
        json_dict['__python_obj__'] = Attacker.__module__ + '.' + Attacker.__name__

        attacker_props = self.convert_props(fake_props=json_dict['theEnvironmentProperties'])
        json_dict['theEnvironmentProperties'] = []

        attacker = json_serialize(json_dict)
        attacker = json_deserialize(attacker)
        attacker.theEnvironmentProperties = attacker_props
        if not isinstance(attacker, Attacker):
            raise MalformedJSONHTTPError(data=request.get_data())
        else:
            return attacker

    def simplify(self, obj):
        assert isinstance(obj, Attacker)
        obj.theEnvironmentDictionary = {}
        obj.likelihoodLookup = {}
        obj.theAttackerPropertyDictionary = {}

        delattr(obj, 'theEnvironmentDictionary')
        delattr(obj, 'likelihoodLookup')
        delattr(obj, 'theAttackerPropertyDictionary')

        obj.theEnvironmentProperties = self.convert_props(real_props=obj.theEnvironmentProperties)

        return obj

    def convert_props(self, real_props=None, fake_props=None):
        new_props = []
        if real_props is not None:
            if len(real_props) > 0:
                for real_prop in real_props:
                    assert isinstance(real_prop, AttackerEnvironmentProperties)
                    capabilities = []
                    for capability in real_prop.theCapabilities:
                        if len(capability) == 2:
                            capabilities.append({
                                'name': capability[0],
                                'value': capability[1]
                            })
                    real_prop.theCapabilities = capabilities
                    new_props.append(real_prop)
        elif fake_props is not None:
            if len(fake_props) > 0:
                for fake_prop in fake_props:
                    check_required_keys(fake_prop, AttackerEnvironmentPropertiesModel.required)
                    cap_list = []
                    assert isinstance(cap_list, list)
                    for cap in fake_prop['theCapabilities']:
                        cap_list.append((cap['name'], cap['value']))
                    new_prop = AttackerEnvironmentProperties(
                        environmentName=fake_prop['theEnvironmentName'],
                        roles=fake_prop['theRoles'],
                        motives=fake_prop['theMotives'],
                        capabilities=cap_list
                    )
                    new_props.append(new_prop)
        else:
            raise MissingParameterHTTPError(param_names=['real_props', 'fake_props'])

        return new_props