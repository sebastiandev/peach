import os
import flask
from peach import WebHandler
from .api import FlaskApiFactory


class FlaskHandler(WebHandler):

    def __init__(self, api_factory=None):
        super().__init__(api_factory or FlaskApiFactory())

    def get_config(self, config):
        conf = flask.config.Config('/')

        if isinstance(config, dict):
            conf.from_mapping(**config)

        elif os.path.isfile(config):
            conf.from_pyfile(config, silent=False)

        else:
            # Config is a path, whats call in flask, Instance path
            try:
                conf = flask.current_app.config

            except:
                # Trick to let flask automagically load the config file
                app = flask.Flask('Dummy', instance_path=config, instance_relative_config=True)
                app.config.from_object('config')
                app.config.from_pyfile('config.py')
                conf = app.config
                del app

        return conf

    def create_app(self, config):
        app = flask.Flask(__name__)
        app.config = config

        for blueprint in self._factory.build(app):
            app.register_blueprint(blueprint)

        return app

    def run(self, app, host, port):
        app.run(host, port)
