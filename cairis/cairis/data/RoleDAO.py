import ARM
from CairisHTTPError import ARMHTTPError, MalformedJSONHTTPError, MissingParameterHTTPError, ObjectNotFoundHTTPError
from Role import Role
from RoleEnvironmentProperties import RoleEnvironmentProperties
from RoleParameters import RoleParameters
from data.CairisDAO import CairisDAO
from tools.JsonConverter import json_serialize, json_deserialize

__author__ = 'Robin Quetin'


class RoleDAO(CairisDAO):
    def __init__(self, session_id):
        CairisDAO.__init__(self, session_id)

    def get_roles(self, constraint_id=-1, simplify=True):
        roles = self.db_proxy.getRoles(constraint_id)

        if simplify:
            for key in roles:
                roles[key] = self.simplify(roles[key])

        return roles

    def get_role_by_name(self, name, simplify=True):
        found_role = None
        roles = self.db_proxy.getRoles()

        if roles is not None:
            found_role = roles.get(name)

        if found_role is None:
            raise ObjectNotFoundHTTPError('The provided role name')

        if simplify:
            found_role = self.simplify(found_role)

        return found_role

    def get_role_by_id(self, role_id, simplify=True):
        found_role = None
        roles = self.db_proxy.getRoles()
        idx = 0

        while found_role is None and idx < len(roles):
            if roles.values()[idx].theId == role_id:
                found_role = roles.values()[idx]
            idx += 1

        if found_role is None:
            raise ObjectNotFoundHTTPError('The provided role name')

        if simplify:
            found_role = self.simplify(found_role)

        return found_role

    def add_role(self, role, role_props=None):
        """
        Adds a new Role to the database
        :type role_props: RoleEnvironmentProperties
        :type role: Role
        :return Returns the role's new ID
        :rtype int
        """
        try:
            self.db_proxy.nameCheck(role.theName, 'role')
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)

        role_params = RoleParameters(
            name=role.theName,
            rType=role.theType,
            sCode=role.theShortCode,
            desc=role.theDescription,
            cProperties=[]
        )

        role_id = self.db_proxy.addRole(role_params)

        if role_props is not None and isinstance(role_props, list):
            role_params.setId(role_id)
            self.update_role_properties(role_props, existing_params=role_params)

        return role_id

    def update_role(self, role, name=None, role_id=-1, role_props=None):
        if name is not None:
            old_role = self.get_role_by_name(name, simplify=False)
            if role is None:
                raise ObjectNotFoundHTTPError('The asset')
            role_id = old_role.theId

        if role_id > -1:
            params = RoleParameters(
                name=role.theName,
                rType=role.theType,
                sCode=role.theShortCode,
                desc=role.theDescription,
                cProperties=[]
            )
            params.setId(id)

            if role_props is not None:
                params.theEnvironmentProperties = role_props

            try:
                self.db_proxy.updateAsset(params)
            except ARM.DatabaseProxyException as ex:
                raise ARMHTTPError(ex)
        else:
            raise MissingParameterHTTPError(param_names=['id'])

    def get_role_props(self, name, simplify=True):
        role = self.get_role_by_name(name, simplify=False)
        props = role.theEnvironmentProperties
        return props

    def update_role_properties(self, props, name=None, role_id=-1, existing_params=None):
        if existing_params is None:
            if role_id > -1:
                role = self.get_role_by_id(role_id, simplify=False)
            elif name is not None:
                role = self.get_role_by_name(name, simplify=False)
            else:
                raise MissingParameterHTTPError(param_names=['name'])

            if role is None:
                raise ObjectNotFoundHTTPError('The asset')

            existing_params = RoleParameters(
                name=role.theName,
                rType=role.theType,
                sCode=role.theShortCode,
                desc=role.theDescription,
                cProperties=[]
            )
            existing_params.setId(role.theId)

        existing_params.theEnvironmentProperties = props

        try:
            self.db_proxy.updateAsset(existing_params)
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)

    def delete_role(self, name=None, role_id=-1):
        if name is not None:
            found_role = self.get_role_by_name(name)
        elif role_id > -1:
            found_role = self.get_role_by_id(role_id)
        else:
            raise MissingParameterHTTPError(param_names=['name'])

        if found_role is None or not isinstance(found_role, Role):
            raise ObjectNotFoundHTTPError('The provided role name')

        try:
            self.db_proxy.deleteRole(found_role.theId)
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)

    def from_json(self, request, to_props=False):
        """
        :rtype tuple
        """
        json = request.get_json(silent=True)
        if json is False or json is None:
            raise MalformedJSONHTTPError(data=request.get_data())

        json_dict = json['object']
        if to_props:
            json['property_0'] = json['object']
        else:
            json_dict['__python_obj__'] = Role.__module__+'.'+Role.__name__
        role = json_serialize(json_dict)
        role_props = json.get('property_0', None)

        if role_props is not None:
            for idx1 in range(0, len(role_props)):
                assert isinstance(role_props[idx1], RoleEnvironmentProperties)
                role_props[idx1]['__python_obj__'] = RoleEnvironmentProperties.__module__+'.'+RoleEnvironmentProperties.__name__
                responses = role_props[idx1]['theResponses']
                if len(responses) > 0:
                    for idx2 in range(0, len(responses)):
                        if isinstance(responses[idx2], list):
                            responses[idx2] = tuple(responses[idx2])
                role_props[idx1]['theResponses'] = responses

            role_props = json_serialize(role_props)
            role_props = json_deserialize(role_props)

        role = json_deserialize(role)
        if not isinstance(role, Role):
            raise MalformedJSONHTTPError(data=request.get_data())
        else:
            return role, role_props

    def simplify(self, obj):
        """
        :type obj: Role
        """
        obj.theEnvironmentDictionary = {}
        obj.theEnvironmentProperties = []
        return obj
