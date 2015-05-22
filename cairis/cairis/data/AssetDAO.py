import numpy
from numpy.core.multiarray import array
import ARM
from Asset import Asset
from AssetEnvironmentProperties import AssetEnvironmentProperties
from AssetParameters import AssetParameters
from CairisHTTPError import ObjectNotFoundHTTPError, MalformedJSONHTTPError, ARMHTTPError, SilentHTTPError, \
    MissingParameterHTTPError, OverwriteNotAllowedHTTPError
from ValueType import ValueType
from ValueTypeParameters import ValueTypeParameters
import armid
from data.CairisDAO import CairisDAO
from tools.JsonConverter import json_serialize, json_deserialize
from tools.ModelDefinitions import AssetEnvironmentPropertiesModel, SecurityAttribute, AssetModel
from tools.SessionValidator import check_required_keys

__author__ = 'Robin Quetin'

class AssetDAO(CairisDAO):
    def __init__(self, session_id):
        CairisDAO.__init__(self, session_id)
        self.prop_values = ['None', 'Low', 'Medium', 'High']
        self.attr_dict = {
            'Confidentiality': armid.C_PROPERTY,
            'Integrity': armid.I_PROPERTY,
            'Availability': armid.AV_PROPERTY,
            'Accountability': armid.AC_PROPERTY,
            'Anonymity': armid.AN_PROPERTY,
            'Pseudonymity': armid.PAN_PROPERTY,
            'Unlinkability': armid.UNL_PROPERTY,
            'Unobservability': armid.UNO_PROPERTY
        }

    def get_assets(self, constraint_id=-1, simplify=True):
        try:
            assets = self.db_proxy.getAssets(constraint_id)
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)

        if simplify:
            for key, value in assets.items():
                assets[key] = self.simplify(value)

        return assets

    def get_asset_by_id(self, id, simplify=True):
        found_asset = None
        try:
            assets = self.db_proxy.getAssets()
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)

        idx = 0
        while found_asset is None and idx < len(assets):
            if assets.values()[idx].theId == id:
                found_asset = assets.values()[idx]
            idx += 1

        if found_asset is None:
            raise ObjectNotFoundHTTPError('The provided asset ID')

        if simplify:
            found_asset = self.simplify(found_asset)

        return found_asset

    def get_asset_by_name(self, name, simplify=True):
        found_asset = None
        try:
            assets = self.db_proxy.getAssets()
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)

        if assets is not None:
            found_asset = assets.get(name)

        if found_asset is None:
            raise ObjectNotFoundHTTPError('The provided asset name')

        if simplify:
            found_asset = self.simplify(found_asset)

        return found_asset

    def get_asset_props(self, name, simplify=True):
        asset = self.get_asset_by_name(name, simplify=False)
        props = asset.theEnvironmentProperties

        if simplify:
            props = self.simplify_props(props)

        return props

    def add_asset(self, asset, asset_props=None):
        try:
            self.db_proxy.nameCheck(asset.theName, 'asset')
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)

        assetParams = AssetParameters(
            assetName=asset.theName,
            shortCode=asset.theShortCode,
            assetDesc=asset.theDescription,
            assetSig=asset.theSignificance,
            assetType=asset.theType,
            cFlag=asset.isCritical,
            cRationale=asset.theCriticalRationale,
            tags=asset.theTags,
            ifs=asset.theInterfaces,
            cProperties=[]
        )

        asset_id = self.db_proxy.addAsset(assetParams)

        if asset_props is not None and isinstance(asset_props, list):
            assetParams.setId(asset_id)
            self.update_asset_properties(asset_props, existing_params=assetParams)

        return asset_id

    def update_asset(self, asset, name=None, id=-1, asset_props=None):
        if name is not None:
            old_asset = self.get_asset_by_name(name, simplify=False)
            if asset is None:
                raise ObjectNotFoundHTTPError('The asset')
            id = old_asset.theId

        if id > -1:
            params = AssetParameters(
                assetName=asset.theName,
                shortCode=asset.theShortCode,
                assetDesc=asset.theDescription,
                assetSig=asset.theSignificance,
                assetType=asset.theType,
                cFlag=asset.isCritical,
                cRationale=asset.theCriticalRationale,
                tags=asset.theTags,
                ifs=asset.theInterfaces,
                cProperties=[]
            )
            params.setId(id)

            if asset_props is not None:
                asset_props = self.expand_props(asset_props)
                params.theEnvironmentProperties = asset_props

            try:
                self.db_proxy.updateAsset(params)
            except ARM.DatabaseProxyException as ex:
                raise ARMHTTPError(ex)
        else:
            raise MissingParameterHTTPError(param_names=['id'])

    def update_asset_properties(self, props, id=-1, name=None, existing_params=None):
        if existing_params is None:
            if id > -1:
                asset = self.get_asset_by_id(id, simplify=False)
            elif name is not None:
                asset = self.get_asset_by_name(name, simplify=False)
            else:
                raise MissingParameterHTTPError(param_names=['name'])

            if asset is None:
                raise ObjectNotFoundHTTPError('The asset')

            existing_params = AssetParameters(
                assetName=asset.theName,
                shortCode=asset.theShortCode,
                assetDesc=asset.theDescription,
                assetSig=asset.theSignificance,
                assetType=asset.theType,
                cFlag=asset.isCritical,
                cRationale=asset.theCriticalRationale,
                tags=asset.theTags,
                ifs=asset.theInterfaces,
                cProperties=[]
            )
            existing_params.setId(asset.theId)

        props = self.expand_props(props)
        existing_params.theEnvironmentProperties = props

        try:
            self.db_proxy.updateAsset(existing_params)
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)

    def delete_asset(self, name=None, asset_id=-1):
        if name is not None:
            found_asset = self.get_asset_by_name(name)
        elif asset_id > -1:
            found_asset = self.get_asset_by_id(asset_id)
        else:
            raise MissingParameterHTTPError(param_names=['name'])

        if found_asset is None or not isinstance(found_asset, Asset):
            raise ObjectNotFoundHTTPError('The provided asset name')

        try:
            self.db_proxy.deleteAsset(found_asset.theId)
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)

    # region Asset Types
    def get_asset_types(self, environment_name=''):
        try:
            asset_types = self.db_proxy.getValueTypes('asset_type', environment_name)
            return asset_types
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)

    def get_asset_type_by_name(self, name, environment_name=''):
        found_type = None
        asset_types = self.get_asset_types(environment_name=environment_name)

        if asset_types is None or len(asset_types) < 1:
            raise ObjectNotFoundHTTPError('Asset types')

        idx = 0
        while found_type is None and idx < len(asset_types):
            if asset_types[idx].theName == name:
                found_type = asset_types[idx]
            idx += 1

        if found_type is None:
            raise ObjectNotFoundHTTPError('The provided asset type name')

        return found_type

    def add_asset_type(self, asset_type, environment_name=''):
        assert isinstance(asset_type, ValueType)
        type_exists = self.check_existing_asset_type(asset_type.theName, environment_name=environment_name)

        if type_exists:
            raise OverwriteNotAllowedHTTPError(obj_name='The asset type')

        params = ValueTypeParameters(
            vtName=asset_type.theName,
            vtDesc=asset_type.theDescription,
            vType='asset_type',
            envName=environment_name,
            vtScore=asset_type.theScore,
            vtRat=asset_type.theRationale
        )

        try:
            return self.db_proxy.addValueType(params)
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)

    def update_asset_type(self, asset_type, name, environment_name=''):
        assert isinstance(asset_type, ValueType)

        found_type = self.get_asset_type_by_name(name, environment_name)

        params = ValueTypeParameters(
            vtName=asset_type.theName,
            vtDesc=asset_type.theDescription,
            vType='asset_type',
            envName=environment_name,
            vtScore=asset_type.theScore,
            vtRat=asset_type.theRationale
        )
        params.setId(found_type.theId)

        try:
            self.db_proxy.updateValueType(params)
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)

    def delete_asset_type(self, name, environment_name=''):
        found_type = self.get_asset_type_by_name(name, environment_name)

        try:
            self.db_proxy.deleteAssetType(found_type.theId)
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)

    def check_existing_asset_type(self, name, environment_name):
        try:
            self.get_asset_type_by_name(name, environment_name)
            return True
        except ObjectNotFoundHTTPError:
            return False
    # endregion

    # region Asset values
    def get_asset_values(self, environment_name=''):
        try:
            asset_values = self.db_proxy.getValueTypes('asset_value', environment_name)
            return asset_values
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)

    def get_asset_value_by_name(self, name, environment_name=''):
        found_value = None
        asset_values = self.get_asset_values(environment_name=environment_name)
        if asset_values is None or len(asset_values) < 1:
            raise ObjectNotFoundHTTPError('Asset values')
        idx = 0
        while found_value is None and idx < len(asset_values):
            if asset_values[idx].theName == name:
                found_value = asset_values[idx]
            idx += 1
        if found_value is None:
            raise ObjectNotFoundHTTPError('The provided asset value name')
        return found_value

    def update_asset_value(self, asset_value, name, environment_name=''):
        assert isinstance(asset_value, ValueType)
        found_value = self.get_asset_value_by_name(name, environment_name)
        params = ValueTypeParameters(
            vtName=asset_value.theName,
            vtDesc=asset_value.theDescription,
            vType='asset_value',
            envName=environment_name,
            vtScore=asset_value.theScore,
            vtRat=asset_value.theRationale
        )
        params.setId(found_value.theId)
        try:
            self.db_proxy.updateValueType(params)
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)

    def check_existing_asset_value(self, name, environment_name):
        try:
            self.get_asset_value_by_name(name, environment_name)
            return True
        except ObjectNotFoundHTTPError:
            return False
    # endregion

    def simplify_props(self, props):
        envPropertiesDict = dict()
        for envProperty in props:
            assert isinstance(envProperty, AssetEnvironmentProperties)
            envPropertyDict = envPropertiesDict.get(envProperty.theEnvironmentName,
                                                    AssetEnvironmentPropertiesModel(envProperty.theEnvironmentName))
            syProperties = envProperty.properties()
            pRationale = envProperty.rationale()
            cProperty = syProperties[armid.C_PROPERTY]
            cRationale = pRationale[armid.C_PROPERTY]
            if cProperty != armid.NONE_VALUE:
                prop_name = 'Confidentiality'
                attr = SecurityAttribute(prop_name, self.prop_values[cProperty], cRationale)
                envPropertyDict.attributesDictionary[prop_name] = attr

            iProperty = syProperties[armid.I_PROPERTY]
            iRationale = pRationale[armid.I_PROPERTY]
            if iProperty != armid.NONE_VALUE:
                prop_name = 'Integrity'
                attr = SecurityAttribute(prop_name, self.prop_values[iProperty], iRationale)
                envPropertyDict.attributesDictionary[prop_name] = attr

            avProperty = syProperties[armid.AV_PROPERTY]
            avRationale = pRationale[armid.AV_PROPERTY]
            if avProperty != armid.NONE_VALUE:
                prop_name = 'Availability'
                attr = SecurityAttribute(prop_name, self.prop_values[avProperty], avRationale)
                envPropertyDict.attributesDictionary[prop_name] = attr

            acProperty = syProperties[armid.AC_PROPERTY]
            acRationale = pRationale[armid.AC_PROPERTY]
            if acProperty != armid.NONE_VALUE:
                prop_name = 'Accountability'
                attr = SecurityAttribute(prop_name, self.prop_values[acProperty], acRationale)
                envPropertyDict.attributesDictionary[prop_name] = attr

            anProperty = syProperties[armid.AN_PROPERTY]
            anRationale = pRationale[armid.AN_PROPERTY]
            if anProperty != armid.NONE_VALUE:
                prop_name = 'Anonymity'
                attr = SecurityAttribute(prop_name, self.prop_values[anProperty], anRationale)
                envPropertyDict.attributesDictionary[prop_name] = attr

            panProperty = syProperties[armid.PAN_PROPERTY]
            panRationale = pRationale[armid.PAN_PROPERTY]
            if panProperty != armid.NONE_VALUE:
                prop_name = 'Pseudonymity'
                attr = SecurityAttribute(prop_name, self.prop_values[panProperty], panRationale)
                envPropertyDict.attributesDictionary[prop_name] = attr

            unlProperty = syProperties[armid.UNL_PROPERTY]
            unlRationale = pRationale[armid.UNL_PROPERTY]
            if unlProperty != armid.NONE_VALUE:
                prop_name = 'Unlinkability'
                attr = SecurityAttribute(prop_name, self.prop_values[unlProperty], unlRationale)
                envPropertyDict.attributesDictionary[prop_name] = attr

            unoProperty = syProperties[armid.UNO_PROPERTY]
            unoRationale = pRationale[armid.UNO_PROPERTY]
            if unoProperty != armid.NONE_VALUE:
                prop_name = 'Unobservability'
                attr = SecurityAttribute(prop_name, self.prop_values[unoProperty], unoRationale)
                envPropertyDict.attributesDictionary[prop_name] = attr

            if envProperty.theAssociations is not None:
                envPropertyDict.associations = envProperty.theAssociations

            envPropertyDict.json_prepare()
            envPropertiesDict[envProperty.theEnvironmentName] = envPropertyDict

        return envPropertiesDict.values()

    def expand_props(self, new_env_props):
        values = ['None', 'Low', 'Medium', 'High']
        envProperties = []
        class_def = AssetEnvironmentPropertiesModel.__module__ + '.' + AssetEnvironmentPropertiesModel.__name__

        for new_env_prop in new_env_props:
            obj_def = new_env_prop.__class__.__module__ + '.' + new_env_prop.__class__.__name__
            if class_def != obj_def:
                raise MalformedJSONHTTPError()
            env_name = new_env_prop.environment

            # Associations should be a list of tuples
            associations = list()
            for idx in range(0, len(new_env_prop.associations)):
                associations.append(tuple(new_env_prop.associations[idx]))

            # Security attributes are represented by properties and rationales
            properties = array([0]*8).astype(numpy.int32)
            rationales = 8 * ['None']
            for attribute in new_env_prop.attributes:
                assert isinstance(attribute, SecurityAttribute)
                prop_id = self.attr_dict.get(attribute.name)
                if -1 > prop_id > 8:
                    msg = 'Invalid attribute index (index={0}). Attribute is being ignored.'.format(attribute.id)
                    raise SilentHTTPError(message=msg)
                value = attribute.get_attr_value(values)
                properties[prop_id] = value
                rationales[prop_id] = attribute.rationale

            env_prop = AssetEnvironmentProperties(env_name, properties, rationales, associations)
            envProperties.append(env_prop)

        return envProperties

    def from_json(self, request, to_props=False):
        self.logger.debug('Request data: %s', request.data)
        json = request.get_json(silent=True)
        if json is False or json is None:
            raise MalformedJSONHTTPError(data=request.get_data())

        json_dict = json['object']
        if to_props:
            if not isinstance(json['object'], list):
                raise MalformedJSONHTTPError(data=request.get_data())
            else:
                for idx in range(0, len(json_dict)):
                    check_required_keys(json_dict[idx], AssetEnvironmentPropertiesModel.required)
                    json_dict[idx]['__python_obj__'] = AssetEnvironmentPropertiesModel.__module__+'.'+AssetEnvironmentPropertiesModel.__name__

            json['property_0'] = json_dict
        else:
            check_required_keys(json_dict, AssetModel.required)
            json_dict['__python_obj__'] = Asset.__module__+'.'+Asset.__name__
        new_json_asset = json_serialize(json_dict)
        new_json_asset_props = json.get('property_0', None)

        if new_json_asset_props is not None:
            for idx1 in range(0, len(new_json_asset_props)):
                check_required_keys(new_json_asset_props[idx1], AssetEnvironmentPropertiesModel.required)
                new_json_asset_props[idx1]['__python_obj__'] = AssetEnvironmentPropertiesModel.__module__+'.'+AssetEnvironmentPropertiesModel.__name__
                attrs = new_json_asset_props[idx1].get('attributes', [])
                for idx2 in range(0, len(attrs)):
                    check_required_keys(attrs[idx2], SecurityAttribute.required)
                    attrs[idx2]['__python_obj__'] = SecurityAttribute.__module__+'.'+SecurityAttribute.__name__
                new_json_asset_props[idx1]['attributes'] = attrs

            new_json_asset_props = json_serialize(new_json_asset_props)
            new_json_asset_props = json_deserialize(new_json_asset_props)

        asset = json_deserialize(new_json_asset)
        if not isinstance(asset, Asset) and not to_props:
            raise MalformedJSONHTTPError(data=request.get_data())
        else:
            return asset, new_json_asset_props

    def simplify(self, asset):
        """
        Simplifies the Asset object by removing the environment properties
        :param asset: The Asset to simplify
        :type asset: Asset
        :return: The simpliefied Asset
        :rtype: Asset
        """
        assert isinstance(asset, Asset)
        asset.theEnvironmentDictionary = {}
        asset.theAssetPropertyDictionary = {}
        asset.theEnvironmentProperties = []
        return asset