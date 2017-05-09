#!/usr/bin/env python
from peach import Peach
from peach.handlers.flask import FlaskHandler
from peach.utils import module_dir


Peach.init(config=module_dir(__file__), handler=FlaskHandler())


from peach.models import BaseModel
from peach.rest.serializers import ModelSerializer, fields
from peach.filters.mongo import NameFilter
from peach.filters import BaseFilter
from peach.handlers.flask.resource import FlaskBaseResource


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


if __name__ == '__main__':
    Peach().run()
