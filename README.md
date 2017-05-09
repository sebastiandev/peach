![Peach](https://github.com/sebastiandev/peach/raw/master/docs/logo.png)

Peaches are sweet and awesome with a strong core, and so is **Peach** which is built on top of great frameworks with a 
touch of magic to make building apis less tedious, letting you focus on the business logic rather than on the database
abstractions, endpoint routing and configurations, blueprint definitions or request parsing.

Many times you have an idea or prototype you want to code but you haven't decide yet which is the web framework that
best suits your needs. Switching from one framework to another is time consuming because you have to
adapt your logic with the new frameworks design, and one doesn't usually code thinking about switching frameworks.

**Peach** was designed in a way that it can sit on top of a framework without affecting the way you code your business
logic, allowing to implement an api that would run on different frameworks, with almost zero code changes.
This is possible because lightweight frameworks are mostly about dealing with requests and responses, so once you
abstract that from your design, you are almost framework agnostic (not 100% but pretty close).


So far **Peach** works with:
  - [Flask](https://github.com/pallets/flask) 
  - [Falcon](https://github.com/falconry/falcon) 


**Peach** also comes with some nice out of the box features such as automagic wiring between resource, models, database
and model filtering. If you like some of Django's magic, but love flask and its minimalistic philosophy, then you'll
love **Peach**.

**Peach** runs on python3 so in order to install, do:

```shell
sudo pip3 install python-peach
```

Tired of reading docs? Okay, here's a full example of a very simple api from scratch

```python

import os
from peach import Peach
from peach.handlers.flask import FlaskHandler
from peach.utils import module_dir


Peach.init(config=os.path.dirname(module_dir(__file__)), handler=FlaskHandler())  # Path to the config.py file directory


from peach.handlers.flask.resource import FlaskBaseResource
from peach.rest.seralizers import ModelSerializer
from peach.filters.mongo import NameFilter
from peach.models import BaseModel
from marshmallow import fields


class People(BaseModel):

    collection_name = 'people'

    def __init__(self, name=None, age=None, address=None, **kwargs):
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

    name = 'address'
    value_type = str
    allow_multiple = False

    @classmethod
    def condition(cls, address):
        return {
            'address': {
                "$regex": ".*?{}.*?".format(address),
                "$options": 'si'
            }
        }


class PeopleResource(FlaskBaseResource):

    model = People
    serializer = PeopleSerializer
    filters = [NameFilter, AddressFilter]
    

if __name__ == '__main__':
    Peach().run(port=3000, host='0.0.0.0')
```

There's only one more file needed, which is the config file. 

If you use Flask, You may have read about the configuring options, there's
usually a config file placed under the source folder. For more info read
[here](http://flask.pocoo.org/docs/0.12/config/#configuring-from-files)


```python
APIS = {
    'api': {
        'prefix': '/api',
        'name': 'People Api',
        'version': '0.0.1',
        'endpoints': [
            {
                'name': 'people',
                'class': 'myapp.app.PeopleResource',
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
    'name': 'PeopleDB'
}
```

That's all you need to get your api up and running! Sweet.

Have some time to read and want to learn more about it? Let's analyze each part of the example

# Models
Just like in any other framework there are models, these are usually very dependent on the database engine mostly
because of the CRUD operations performed on the database. **Peach** offers a base class for models that abstracts many
of the internals of accesing the database, and it also offers a
[proxy](https://github.com/sebastiandev/peach/raw/master/peach/database/proxy.py), with whom the base model interacts
with, allowing to interact in the same way with different database engines. So far there's only one implementation of
a proxy, and it is for [MongoDB](https://github.com/sebastiandev/peach/raw/master/peach/database/mongo_proxy.py)

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
Here we have defined the People model, since we are working with MongoDB we need to specify a collection name. Then the
 basic operations are already implemented on the MongoDBProxy. If any other method is needed, like a more complex query
 using aggregation, it can be added on your model.

# Serializers
For every model, there's usually a serializer that handles the representation of the model as a json document. The base
 serialization class is based on [marshmallow](https://github.com/marshmallow-code/marshmallow), and it only requires
you to specify the model is serializing and the fields you want to use from the model

``` python
class PeopleSerializer(ModelSerializer):

    model = People

    name = fields.String()
    age = fields.Int()
    address = fields.String()
``` 

# Filters
Filters are as the name suggests a way of filtering models but in a more decoupled way, so one filter might be re used
on different models that share the same attribute, like date, name, or any other you may come up with. They are
designed around the idea of applying a condition over a data collection, so, in order to create a filter you need to
give it a name, to be identifiable, define the type of the attribute to filter and specify if the filter allows
multiple values or not.

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
The [BaseFilter](https://github.com/sebastiandev/peach/raw/master/peach/filters/__init__.py) class has 3 methods,
one builds the condition, another applies the condition on the model and the third counts the amount of docs that
satisfiy the condition. Similar to models, filters depend on the database engine, thus the condition will be the method
you will always need to override to build the condition in the database sintax. There are some generic filters for mongo
 db already implemented.

# Resources
Sometimes called views in a more simplified version, represent the actual thing (usually a model) you want to operate
on. In our example we are dealing with people. Every resource of course has an endpoint and handles certain common
operations like paging, sorting and filtering.

```python
from peach.web.flask.resource import FlaskBaseResource


class PeopleResource(FlaskBaseResource):

    model = People
    serializer = PeopleSerializer
    filters = [NameFilter, AddressFilter]
```

or if you prefer Falcon
```python
from peach.handlers.falcon.resource import FalconBaseResource


class PeopleResource(FalconBaseResource):

    model = People
    serializer = PeopleSerializer
    filters = [NameFilter, AddressFilter]
```

The base class for resources [BaseResource](https://github.com/sebastiandev/peach/raw/master/peach/rest/resource.py)
handles all the wiring for the most basic operations. All you need to do in the most simple case is define the model, 
the serializer to be used and the available filters.

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

If you need your results to be sorted by any of the model attributes, you can do it by using the sort keyword.

```shell
curl -GET localhost:3000/api/people?filter[name]=foo&sort=name
curl -GET localhost:3000/api/people?page[size]=20&sort=<name,>age
```

You can specify the ordering by prepending < (Descending) or > (Ascending) the attribute name. You can combine sorting
 with different attributes by specifying more attributes as a comma separated list.

# Running your app
In order to run your app you need to create the application object. Before doing anything, and after importing peach,
you **MUST** define the path for you config file. This is usually placed under the source directory.
If you have a script that populates your database or does anything that deals with models, you **MUST** initialize
peach with the *instance_path* before doing anything or importing any model.

## Initialization
For the configuration you can use the flask standard way of defining instance's path, or you can pass the absolute
path to your config file or you can pass a dictionary. Did I say that this is the first thing you **MUST** do after
import peach? Yeah...


```python
from peach import Peach
from peach.handlers.flask import FlaskHandler
from peach.utils import module_dir

# The usual flask way
Peach.init(config=module_dir(__file__), handler=FlaskHandler())  # here the path is taken from the current file

# Using falcon
from peach.handlers.falcon import FalconHandler
import config
Peach.init(config=config, handler=FalconHandler())  # here the path is taken from the current file


# Using a custom file (variable names should always be in CAPITALS)
Peach.init(config=path_to_a_file, handler=FalconHandler())  # This should be an absolute path to a file

# Using a dict (variable names should always be in CAPITALS)
Peach.init(config={}, handler=FalconHandler())  # A standard dict, maybe usefull for test cases


# Do whatever you need now ...

Peach().run(port=3000, host='0.0.0.0') 
```

# Customizations
There are always corner cases or different needs that require changes. **Peach** offers a good balance between
features, organization and soft rules to allow for further customizations without forcing the code changes to be
overcomplicated or look like ad hoc hacks. Nevertheless, there are better places than others to make the needed
changes or extensions and here you will get an idea of possible extensions and the best place to put them.

## Pagination
**Peach** ships with built in pagination but you can provide you own logic as needed. When building the api, some
objects are injected to the base resource like the databae proxy, the response factory and the pagination class. If
you want to provide your own pagination, simply add one line in your api configuration specifying the module path for
you pagination.

```python
APIS = {
    'api': {
        'prefix': '/api',
        'name': 'People Api',
        'version': '0.0.1',
        'pagination': 'peach.rest.pagination.Pagination',
        'endpoints': [
            {
                'name': 'people',
                'class': 'myapp.app.PeopleResource',
                'urls': [
                    '/people',
                    '/people/<string:ids>'
                ]
            }
         ]
    }
}
```

## Response formats
The response is a way of rendering the returned data from the api. There are many ways of formating a response.
A popular one is JSONApi but it is also a very robust and copmlex format. The default response format used in **Peach**
 resembles a bit of JSONApi but just a bit, if you need to implement something like that or any other formating, the
best place to put this is as a new response class. For this you need to define the response factory in the api
configuration

```python
APIS = {
    'api': {
        'prefix': '/api',
        'name': 'People Api',
        'version': '0.0.1',
        'response_factory': 'peach.rest.response.ResponseFactory',
        'endpoints': [
            {
                'name': 'people',
                'class': 'myapp.app.PeopleResource',
                'urls': [
                    '/people',
                    '/people/<string:ids>'
                ]
            }
         ]
    }
}
```
The response factory receives the data to render, any metadata needed to be displayed (in a form of a dict), a
pagination object and a variable kwargs for any extra parameters. With this you should be able to render your custom
response. Of course, following the JSONApi format, the very same resource seriralization requires a specific formating
and to accomplish this you also need to define your model serialization accordingly (for this you'll probably need to
dive deeper into marshmallow)

## More dependencies for your resources
If need to inject more objects/modules to your resources, just extend the
[ApiFactory](https://github.com/sebastiandev/peach/raw/master/peach/rest/api.py), extending for you selected framework,
 flaskand or falcon, and override the *load_api_resource_params* method to populate the Conf object with whatever you 
need. This method receives the app and the api configuration defined in the config.py module.

```python
from peach.handlers.flask.api import FlaskApiFactory


class MyApiFactory(FlaskApiFactory):

    @classmethod
    def load_api_resource_params(cls, app_conf, api_conf):
        conf = super().load_conf(app_conf, api_conf)
        # add your stuff here
        
        return conf
```

And then pass it when initializing the handler fro you peach app

```python
from peach import Peach
from peach.handlers.flask import FlaskHandler

Peach.init(config=config, handler=FlaskHandler(MyApiFactory()))
```
