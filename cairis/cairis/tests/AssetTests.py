import logging
from urllib import quote
import jsonpickle
from Asset import Asset
import cairisd
import unittest
from tools.JsonConverter import json_deserialize
from tools.ModelDefinitions import AssetEnvironmentPropertiesModel, AssetSecurityAttribute

__author__ = 'Robin Quetin'


class AssetTests(unittest.TestCase):
    # region Class fields
    app = cairisd.start(['-d', '--unit-test'])
    logger = logging.getLogger('AssetTests')
    new_asset = Asset(
        assetId=-1,
        assetName='Test',
        shortCode='TST',
        assetDescription='This is a new test asset',
        assetSig='Very significant',
        assetType='Hardware',
        cFlag=0,
        cRationale=None,
        tags=[],
        ifs=[],
        cProps=[]
    )
    new_asset_sec_attr = [
        AssetSecurityAttribute(
            'Accountability',
            'Low',
            'None'
        ),
        AssetSecurityAttribute(
            'Confidentiality',
            'Medium',
            'None'
        )
    ]
    new_asset_props = [
        AssetEnvironmentPropertiesModel(
            env_name='Stroke',
            attributes=new_asset_sec_attr
        )
    ]
    new_asset_dict = {
        'session_id': 'test',
        'object': new_asset,
        'property_0': new_asset_props
    }
    new_asset_body = jsonpickle.encode(new_asset_dict)
    # endregion
    logger.info('JSON data: %s', new_asset_body)

    def test_get_all(self):
        method = 'test_get_all'
        rv = self.app.get('/api/assets?session_id=test')
        assets = json_deserialize(rv.data)
        self.assertIsNotNone(assets, 'No results after deserialization')
        self.assertIsInstance(assets, dict, 'The result is not a dictionary as expected')
        self.assertGreater(len(assets), 0, 'No assets in the dictionary')
        self.assertIsInstance(assets.values()[0], Asset)
        self.logger.info('[%s] Assets found: %d', method, len(assets))
        self.logger.info('[%s] First asset: %s [%d]', method, assets.values()[0].theName, assets.values()[0].theId)

    def test_post(self):
        method = 'test_post_new'
        rv = self.app.post('/api/assets', content_type='application/json', data=self.new_asset_body)
        self.logger.info('[%s] Response data: %s', method, rv.data)
        json_resp = json_deserialize(rv.data)
        self.assertIsNotNone(json_resp, 'No results after deserialization')
        asset_id = json_resp.get('asset_id', None)
        self.assertIsNotNone(asset_id, 'No asset ID returned')

        rv = self.app.get('/api/assets/id/%d?session_id=test' % asset_id)
        asset = json_deserialize(rv.data)
        self.logger.info('[%s] Asset: %s [%d]', method, asset.theName, asset.theId)

    def test_get_id(self):
        method = 'test_get_id'
        rv = self.app.get('/api/assets/id/127?session_id=test')
        asset = json_deserialize(rv.data)
        self.assertIsNotNone(asset, 'No results after deserialization')
        self.assertIsInstance(asset, Asset, 'The result is not an asset as expected')
        self.logger.info('[%s] Asset: %s [%d]', method, asset.theName, asset.theId)

    def test_get_name(self):
        method = 'test_get_name'
        rv = self.app.get('/api/assets/name/Data%20node?session_id=test')
        asset = json_deserialize(rv.data)
        self.assertIsNotNone(asset, 'No results after deserialization')
        self.assertIsInstance(asset, Asset, 'The result is not an asset as expected')
        self.logger.info('[%s] Asset: %s [%d]', method, asset.theName, asset.theId)

    def test_put_name(self):
        method = 'test_put_name'
        url = '/api/assets/name/%s' % quote(self.new_asset.theName)

        upd_asset = self.new_asset
        upd_asset.theName = 'Test2'
        upd_asset_dict = self.new_asset_dict
        upd_asset_dict['object'] = upd_asset
        upd_asset_body = jsonpickle.encode(upd_asset_dict)
        self.logger.info('[%s] JSON data: %s', method, upd_asset_body)

        rv = self.app.put(url, content_type='application/json', data=upd_asset_body)
        self.logger.info('[%s] Response data: %s', method, rv.data)
        json_resp = json_deserialize(rv.data)
        self.assertIsNotNone(json_resp, 'No results after deserialization')
        message = json_resp.get('message', None)
        self.assertIsNotNone(message, 'No message returned')

        rv = self.app.get('/api/assets/name/Test2?session_id=test')
        asset = json_deserialize(rv.data)
        self.logger.info('[%s] Asset: %s [%d]', method, asset.theName, asset.theId)

    def test_delete_name(self):
        method = 'test_delete_name'
        url = '/api/assets/name/{}?session_id=test'.format(quote(self.new_asset.theName))
        rv = self.app.delete(url)
        self.logger.info('[%s] Response data: %s', method, rv.data)
        json_resp = json_deserialize(rv.data)
        self.assertIsNotNone(json_resp, 'No results after deserialization')
        message = json_resp.get('message', None)
        self.assertIsNotNone(message, 'No message returned')
        url = '/api/assets/name/Test2?session_id=test'.format(quote(self.new_asset.theName))
        rv = self.app.delete(url)