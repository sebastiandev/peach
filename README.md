![Peach](https://github.com/sebastiandev/peach/raw/master/docs/logo.png)

Peaches are sweet and awesome with a strong core, and so is **Peach** which is built on top of the beloved [Flask](https://github.com/pallets/flask) and [Flask-restful](https://github.com/flask-restful/flask-restful/) with a touch of magic to make building apis less tedious, letting you focus on the business logic rather than on the database abstractions, endpoint routing and configurations, blueprint definitions or request parsing. 

**Peach** also comes with some nice out of the box features such as automagic wiring between resource, models, database and model filtering. If you like some of Django's magic, but love flask and its minimalistic philosophy, then you'll love **Peach**.

Tired of reading docs? Okay, here's a full example of a very simple api from scratch

```python

from peach.rest.resource import FiltrableResource
from peach.rest.seralizers import ModelSerializer
from peach.filters.mongo import NameFilter
from peach.models import BaseModel
from marshmallow import fields


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
app.run(port=3000, host='0.0.0.0')    
```

There's only one more file needed, which is the config file. You may have read about flask configuring options, theres usually a config file placed under the source folder. For more info read [here](http://flask.pocoo.org/docs/0.12/config/#configuring-from-files)

```python
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

Have some time to read and want to learn more about it? Let's analyze each part of the example

# Models
Just like in any other framework there are models, these are usually very dependent on the database engine mostly because of the CRUD operations performed on the database. **Peach** offers a base class for models that abstracts many of the internals of accesing the database, and it also offers a [proxy](https://github.com/sebastiandev/peach/raw/master/peach/database/proxy.py), with whom the base model interacts with, allowing to interact in the same way with different database engines. So far there's only one implementation of a proxy, and it is for [MongoDB](https://github.com/sebastiandev/peach/raw/master/peach/database/mongo_proxy.py)

```python
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
``` 
Here we have defined the People model, since we are working with MongoDB we need to specify a collection name. Then the basic operations are already implemented on the MongoDBProxy. If any other method is needed, like a more complex query using aggregation, it can be added on your model.

# Serializers
For every model, there's usually a serializer that handles the representation of the model as a json document. The base serialization class is based on [marshmallow](https://github.com/marshmallow-code/marshmallow), and it only requires you to specify the model is serializing and the fields you want to use from the model

``` python
class PeopleSerializer(ModelSerializer):

    model = People

    name = fields.String()
    age = fields.Int()
    address = fields.String()
``` 

# Filters
Filters are as the name suggests a way of filtering models but in a more decoupled way, so one filter might be re used on different models that share the same attribute, like date, name, or any other you may come up with. They are designed around the idea of applying a condition over a data collection, so, in order to create a filter you need to give it a name, to be identifiable, define the type of the attribute to filter and specify if the filter allows multiple values or not. 

```python
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
```
The [BaseFilter](https://github.com/sebastiandev/peach/raw/master/peach/filters/__init__.py) class has 3 methods, one builds the condition, another applies the condition on the model and the third counts the amount of docs that satisfiy the condition. Similar to models, filters depend on the database engine, thus the condition will be the method you will always need to override to build the condition in the database sintax. There are some generic filters for mongo db already implemented.

# Resources
Sometimes called views in a more simplified version, represent the actual thing (usually a model) you want to operate on. In our example we are dealing with people. Every resource of course has an endpoint and handles certain common operations like paging, sorting and filtering. 

```python
class PeopleResource(FiltrableResource):

    model = People
    serializer = PeopleSerializer
    filters = [NameFilter, AddressFilter]
```

The base class for resources [BaseResource](https://github.com/sebastiandev/peach/raw/master/peach/rest/resource.py) handles all the wiring for the most basic operations, if you need to allow filtering, then you need to inherit your resource from [FiltrableResource](https://github.com/sebastiandev/peach/raw/master/peach/rest/resource.py). All you need to do in the most simple case is define the model, the serializer to be used and the avaiable filters.

In order to filter a resource, you need to add the filter the query string like this:

```shell
curl -GET localhost:3000/api/people?filter[name]=foo
curl -GET localhost:3000/api/people?filter[name]=foo,mary
```
The standard sintax is *filter[FILTER NAME]=FILTER VALUE*

If your query/filter returns many results, you can ask for a diffrent page or define the page size like this:

```shell
curl -GET localhost:3000/api/people?filter[name]=foo&page[number]=2  # to get the secondn page
curl -GET localhost:3000/api/people?page[size]=20&page[number]=4  # to use a page size of 20 and get the 4th page
```



