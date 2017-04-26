![Peach](https://github.com/sebastiandev/peach/raw/master/docs/logo.png)

Peaches are sweet and awesome with a strong core, and so is **Peach** which is built on top of the beloved [Flask](https://github.com/pallets/flask) and [Flask-restful](https://github.com/flask-restful/flask-restful/) with a touch of magic to make building apis less tedious, letting you focus on the business logic rather than on the databse abstractions, endpoint routing and configurations, blueprint definitions or request parrsing. It also comes with some nice out of the box funtionalities such as automagic wiring between resource, models, database and model filtering. If you like some of Django's magic, but love flask and its minimalistic philosophy, then you'll love **Peach**.

Tired of reading docs? Okay, here's a full example of a very simple api from scratch

```python

from peach.rest.resource import FiltrableResource
from peach.rest.seralizers import ModelSerializer
from peach.filters.mongo import NameFilter
from peach.models import BaseModel

class People(BaseModel):

    collection_name = 'people'

    def __init__(self, name=None, age=None, addres=None, **kwargs):
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

    name = fields.String()
    age = fields.Int()
    address = fields.String()


class AddressFilter(BaseFilter):

    name = 'addres'
    value_type = str
    allow_multiple = False

    @classmethod
    def condition(cls, address):
        return {
            'account': {
                "$regex": ".*?{}.*?".format(address),
                "$options": 'si'
            }
        }


class PeopleResource(FiltrableResource):

    model = People
    serializer = PeopleSerializer
    filters = [NameFilter, AddressFilter]
    
    
import os
import peach
from peach import create_app
from peach.utils import module_dir


peach.INSTANCE_PATH = os.path.dirname(module_dir(__file__))  # Path to the config.py file directory

app = create_app()
app.run(port=3000, host=0.0.0.0)    
```

Theres only one more file we need, which is the config file. You have read about flask, theres usually a config file placed under the source folder. For more info read [here](http://flask.pocoo.org/docs/0.12/config/#configuring-from-files)

```
APIS = {
    'api': {
        'prefix': '/api',
        'name': 'People Api',
        'version': '0.0.1',
        'endpoints': [
            {
                'name': 'people',
                'class': 'myapp.__init__.PeopleResource',
                'urls': [
                    '/people',
                    '/people/<string:ids>'
                ]
            }
         ]
    }
}


DATABASE = {
    'proxy': 'peach.database.mongo_proxy.MongoDBProxy',
    'uri': 'mongodb://localhost:27017/',
    'name': 'People DB'
}
```

Thats all you need to get your api up and runnig! Sweet.
