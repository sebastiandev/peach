import falcon
import os
from wsgiref import simple_server
from .api import FalconApiFactory
from peach import WebHandler


class FalconHandler(WebHandler):

    def __init__(self, api_factory=None):
        super().__init__(api_factory or FalconApiFactory())

    def _load_config_from_pyfile(self, filename):
        conf = object()

        try:
            with open(filename, mode='rb') as config_file:
                exec(compile(config_file.read(), filename, 'exec'), conf.__dict__)
        except IOError as e:
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise

        return self._config_from_object(conf)

    def _config_from_object(self, obj):
        conf = {}
        for key in dir(obj):
            if key.isupper():
                conf[key] = getattr(obj, key)

        return conf

    def get_config(self, config):
        if isinstance(config, str) and os.path.isfile(config):
            config = self._load_config_from_pyfile(config)

        elif isinstance(config, object):
            config = self._config_from_object(config)

        return config

    def create_app(self, config):
        app = falcon.API()
        self._factory.build(app, config)
        return app

    def run(self, app, host, port):
        httpd = simple_server.make_server(host, port, app)
        httpd.serve_forever()
