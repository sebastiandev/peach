#!/usr/bin/env python
from peach import Peach
from peach.handlers.flask import FlaskHandler
from peach.utils import module_dir


Peach.init(config=module_dir(__file__), handler=FlaskHandler())


from app import People


People.add(People(name='Lionel', age=28, address='Somewhere in Barcelona'))
People.add(People(name='Radamel', age=30, address='Somewhere in Monaco'))
People.add(People(name='Cristiano', age=29, address='Somewhere in Madrid'))
People.add(People(name='Paulo', age=24, address='Somewhere in Italy'))
People.add(People(name='Luis', age=30, address='Somewhere in Barcelona'))
People.add(People(name='Sebastian', age=33, address='Somewhere in Buenos Aires'))
People.add(People(name='Hernan', age=35, address='Somewhere in Italy'))

