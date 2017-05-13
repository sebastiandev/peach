import pytest
import json
from peach import Peach
from peach.handlers.falcon import FalconHandler


test_config = {
    'APIS': {
        'api': {
            'prefix': '/api',
            'name': 'Test Api',
            'version': '0.0.1',
            'pagination': 'peach.rest.pagination.Pagination',
            'response_factory': 'peach.rest.response.ResponseDocumentFactory',
            'endpoints': [
                {
                    'name': 'people',
                    'class': 'tests.test_falcon_resource.PeopleResource',
                    'urls': [
                        '/people',
                        '/people/{ids}'
                    ]
                }
            ]
        },
    },

    'DATABASE': {
        'proxy': 'peach.database.mongo_proxy.MongoDBProxy',
        'uri': 'mongodb://localhost:27017/',
        'name': 'testing'
    }
}


Peach.init(test_config, FalconHandler())


from marshmallow import fields
from pymongo import MongoClient
from peach.rest.serializers import ModelSerializer
from peach.filters import BaseFilter
from peach.models import BaseModel
from peach.handlers.falcon.resource import FalconBaseResource
from peach.filters.mongo import NameFilter
from falcon import testing


class People(BaseModel):

    collection_name = 'people'

    def __init__(self, name=None, age=None, address=None, **kwargs):
        if 'type' in kwargs:
            kwargs.pop('type')

        super().__init__(**{
            'name': name,
            'age': age,
            'address': address
        }, **kwargs)

    @classmethod
    def build(cls, doc):
        return People(**doc) if doc else None


class PeopleSerializer(ModelSerializer):

    model = People

    name = fields.Str(required=True)
    age = fields.Int(required=True)
    address = fields.Str()


class AgeFilter(BaseFilter):

    name = 'age'
    value_type = int
    allow_multiple = False

    @classmethod
    def condition(cls, age):
        return {'age': age}


class PeopleResource(FalconBaseResource):
    model = People
    serializer = PeopleSerializer
    filters = [NameFilter, AgeFilter]


@pytest.fixture
def tester(request):

    People.add(People(name='Foo', age=22, address="xxxx"))
    People.add(People(name='John', age=22, address="yyyy"))
    People.add(People(name='Paul', age=44, address="zzzz"))
    People.add(People(name='David', age=18, address="aaaa"))
    People.add(People(name='Maria', age=27, address="bbbb"))
    People.add(People(name='Jean', age=36, address="cccc"))

    def fin():
        MongoClient(test_config['DATABASE']['uri']).drop_database(test_config['DATABASE']['name'])

    request.addfinalizer(fin)

    return testing.TestClient(Peach().create_app())


def test_get_all(tester):
    response = json.loads(tester.simulate_get('/api/people').content.decode())

    assert 6 == len(response['data'])

    response_people_names = [p['name'] for p in response['data']]
    assert all([name in response_people_names for name in ['Foo', 'John', 'Paul', 'David', 'Maria', 'Jean']])


def test_get_by_name(tester):
    response = json.loads(tester.simulate_get('/api/people', query_string='filter[name]=Foo').content.decode())

    assert 1 == len(response['data'])
    assert 'Foo' == response['data'][0]['name']


def test_get_by_age(tester):
    response = json.loads(tester.simulate_get('/api/people', query_string='filter[age]=22').content.decode())

    assert 2 == len(response['data'])

    response_data_names = [r['name'] for r in response['data']]
    assert all([n in response_data_names for n in ['Foo', 'John']])


def test_get_with_custom_elem_page_size(tester):
    for psize in [1, 2, 3, 4]:
        response = json.loads(tester.simulate_get('/api/people', query_string='page[size]={}'.format(psize)).content.decode())
        assert psize == len(response['data'])


def test_get_sorted(tester):
    # Test ascending sorting
    response = json.loads(tester.simulate_get('/api/people', query_string='sort=name').content.decode())

    assert response['data'][0]['name'] == 'David'
    assert response['data'][-1]['name'] == 'Paul'

    # Test descending sorting
    response = json.loads(tester.simulate_get('/api/people', query_string='sort=<name').content.decode())

    assert response['data'][0]['name'] == 'Paul'
    assert response['data'][-1]['name'] == 'David'

