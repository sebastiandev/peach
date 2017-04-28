#!/usr/bin/env python
import peach
from peach import create_app
from peach.utils import module_dir


peach.INSTANCE_PATH = module_dir(__file__)


from peach.models import BaseModel
from peach.rest.serializers import ModelSerializer, fields
from peach.filters.mongo import NameFilter
from peach.filters import BaseFilter
from peach.rest.resource import FiltrableResource


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


class PeopleResource(FiltrableResource):

    model = People
    serializer = PeopleSerializer
    filters = [NameFilter, AgeFilter]


if __name__ == '__main__':
    app = create_app()

    @app.route("/")
    def main():
        return "people-server"

    app.run(port=3000, host='0.0.0.0')
