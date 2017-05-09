

__version__ = '0.1.0'


class WebHandler(object):

    def __init__(self, api_factory):
        self._factory = api_factory

    def get_config(self, config):
        raise NotImplementedError

    def create_app(self, config):
        raise NotImplementedError


class Peach(object):

    __config = None
    __handler = None

    @classmethod
    def init(cls, config, handler):
        cls.__config = config
        cls.__handler = handler

    def __init__(self):
        if not isinstance(self.__config, dict) and \
           not isinstance(self.__config, str) and \
           not isinstance(self.__config, object):
            raise Exception("Config must be a dict or a path to the config file or directory")

        if not self.__handler:
            raise Exception("Must specify a handler before creating a Peach instance")

    @property
    def config(self):
        return self.__handler.get_config(self.__config)

    @property
    def database_config(self):
        return self.__handler.get_config(self.__config)['DATABASE']

    def create_app(self):
        return self.__handler.create_app(self.config)

    def run(self, host='0.0.0.0', port=3000, app=None):
        app = app or self.create_app()
        self.__handler.run(app, host, port)


