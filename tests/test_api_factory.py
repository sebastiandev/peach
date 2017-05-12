import pytest
from peach.rest.base_api import ApiFactory
from peach.database.mongo_proxy import MongoDBProxy
from peach.rest.pagination import Pagination
from peach.rest.response import ResponseDocumentFactory


@pytest.fixture
def data():

    return {
        'APIS': {
            'api': {
                'prefix': '/api',
                'name': 'Test Api',
                'version': '0.0.1',
                'pagination': 'peach.rest.pagination.Pagination',
                'response_factory': 'peach.rest.response.ResponseDocumentFactory',
                'endpoints': [
                    {
                        'name': 'test-people',
                        'class': 'peach.rest.resource.BaseResource',
                        'urls': [
                            '/people',
                            '/people/<string:ids>'
                        ]
                    }
                ]
            },
            'api_v2': {
                'prefix': '/api/v2',
                'name': 'Test Api 2',
                'version': '0.0.2',
                'pagination': 'peach.rest.pagination.Pagination',
                'response_factory': 'peach.rest.response.ResponseDocumentFactory',
                'endpoints': [
                    {
                        'name': 'test-people',
                        'class': 'peach.rest.resource.BaseResource',
                        'urls': [
                            '/people',
                            '/people/<string:ids>'
                        ]
                    }
                ]
            }

        },

        'DATABASE':  {
            'proxy': 'peach.database.mongo_proxy.MongoDBProxy',
            'uri': 'mongodb://localhost:27017/',
            'name': 'test'
        }
    }


def test_load_api_resource_params(data):
    api_conf = list(data['APIS'].values())[0]
    loaded_conf = ApiFactory().load_api_resource_params(data, api_conf)

    assert 'prefix' in loaded_conf
    assert 'database' in loaded_conf
    assert 'pagination' in loaded_conf
    assert 'response_factory' in loaded_conf

    assert loaded_conf['prefix'] == api_conf['prefix']
    assert isinstance(loaded_conf['database'], MongoDBProxy)
    assert loaded_conf['pagination'] == Pagination
    assert loaded_conf['response_factory'] == ResponseDocumentFactory


def test_load_api_definitions(data):
    api_definitions = ApiFactory()._api_definitions(data)

    assert 2 == len(api_definitions)

    for api_id, api_def in list(api_definitions.items()):
        original_def = data['APIS'][api_id]

        assert api_def.name == original_def['name']
        assert api_def.prefix == original_def['prefix']
        assert api_def.version == original_def['version']
        assert api_def.mediatype == original_def.get('mediatype', None)
        assert len(api_def.endpoints) == len(original_def['endpoints'])

        for ep in api_def.endpoints.values():
            assert ep.name == original_def['endpoints'][0]['name']
            assert ep.urls == original_def['endpoints'][0]['urls']
            assert issubclass(ep.handler, object)
