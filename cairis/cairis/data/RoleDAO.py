import ARM
from CairisHTTPError import ARMHTTPError, MalformedJSONHTTPError, MissingParameterHTTPError, ObjectNotFoundHTTPError
from Role import Role
from RoleEnvironmentProperties import RoleEnvironmentProperties
from RoleParameters import RoleParameters
from data.CairisDAO import CairisDAO
from tools.JsonConverter import json_serialize, json_deserialize
from tools.ModelDefinitions import RoleModel
from tools.SessionValidator import check_required_keys

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
            self.close()
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
            self.close()
            raise ObjectNotFoundHTTPError('The provided role name')

        if simplify:
            found_role = self.simplify(found_role)

        return found_role

    def add_role(self, role):
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
            self.close()
            raise ARMHTTPError(ex)

        role_params = RoleParameters(
            name=role.theName,
            rType=role.theType,
            sCode=role.theShortCode,
            desc=role.theDescription,
            cProperties=[]
        )

        role_id = self.db_proxy.addRole(role_params)

        return role_id

    def update_role(self, role, name=None, role_id=-1):
        if name is not None:
            old_role = self.get_role_by_name(name, simplify=False)
            if role is None:
                self.close()
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
            params.setId(role_id)

            try:
                self.db_proxy.updateRole(params)
            except ARM.DatabaseProxyException as ex:
                self.close()
                raise ARMHTTPError(ex)
        else:
            self.close()
            raise MissingParameterHTTPError(param_names=['id'])

    def get_role_props(self, name):
        role = self.get_role_by_name(name, simplify=False)
        props = role.theEnvironmentProperties
        return props

    def delete_role(self, name=None, role_id=-1):
        if name is not None:
            found_role = self.get_role_by_name(name)
        elif role_id > -1:
            found_role = self.get_role_by_id(role_id)
        else:
            self.close()
            raise MissingParameterHTTPError(param_names=['name'])

        if found_role is None or not isinstance(found_role, Role):
            self.close()
            raise ObjectNotFoundHTTPError('The provided role name')

        try:
            self.db_proxy.deleteRole(found_role.theId)
        except ARM.DatabaseProxyException as ex:
            self.close()
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            self.close()
            raise ARMHTTPError(ex)

    def from_json(self, request):
        """
        :rtype Role
        """
        json = request.get_json(silent=True)
        if json is False or json is None:
            self.close()
            raise MalformedJSONHTTPError(data=request.get_data())

        json_dict = json['object']
        check_required_keys(json_dict, RoleModel.required)
        json_dict['__python_obj__'] = Role.__module__+'.'+Role.__name__
        role = json_serialize(json_dict)
        role = json_deserialize(role)
        if not isinstance(role, Role):
            self.close()
            raise MalformedJSONHTTPError(data=request.get_data())
        else:
            return role

    def simplify(self, obj):
        """
        :type obj: Role
        """
        obj.theEnvironmentDictionary = {}
        obj.theEnvironmentProperties = []
        return obj