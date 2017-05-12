import pytest
import json
from marshmallow import fields
from peach import Peach
from peach.handlers.flask import FlaskHandler
from pymongo import MongoClient


test_config = {
    'TESTING': True,
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
                    'class': 'tests.test_flask_resource.PeopleResource',
                    'urls': [
                        '/people',
                        '/people/<string:ids>'
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

Peach.init(test_config, FlaskHandler())


from peach.handlers.flask.resource import FlaskBaseResource
from peach.rest.serializers import ModelSerializer
from peach.filters import BaseFilter
from peach.filters.mongo import NameFilter
from peach.models import BaseModel


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


class PeopleResource(FlaskBaseResource):
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

    return Peach().create_app().test_client()


def test_get_all(tester):
    response = json.loads(tester.get('/api/people').data)

    assert 6 == len(response['data'])

    response_people_names = [p['name'] for p in response['data']]
    assert all([name in response_people_names for name in ['Foo', 'John', 'Paul', 'David', 'Maria', 'Jean']])


def test_get_by_name(tester):
    response = json.loads(tester.get('/api/people?filter[name]=Foo').data)

    assert 1 == len(response['data'])
    assert 'Foo' == response['data'][0]['name']


def test_get_by_age(tester):
    response = json.loads(tester.get('/api/people?filter[age]=22').data)

    assert 2 == len(response['data'])

    response_data_names = [r['name'] for r in response['data']]
    assert all([n in response_data_names for n in ['Foo', 'John']])


def test_get_with_custom_elem_page_size(tester):
    for psize in [1, 2, 3, 4]:
        response = json.loads(tester.get('/api/people?page[size]={}'.format(psize)).data)
        assert psize == len(response['data'])


def test_get_sorted(tester):
    # Test ascending sorting
    response = json.loads(tester.get('/api/people?sort=name').data)

    assert response['data'][0]['name'] == 'David'
    assert response['data'][-1]['name'] == 'Paul'

    # Test descending sorting
    response = json.loads(tester.get('/api/people?sort=<name').data)

    assert response['data'][0]['name'] == 'Paul'
    assert response['data'][-1]['name'] == 'David'


