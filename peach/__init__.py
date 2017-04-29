import flask
from peach.rest.api import ApiFactory


INSTANCE_PATH = None
INSTANCE_CONFIG = None


def init_peach(instance_path=None, config=None):
    global INSTANCE_PATH
    global INSTANCE_CONFIG

    if instance_path:
        INSTANCE_PATH = instance_path

    elif config:
        INSTANCE_CONFIG = config


def get_config():
    if INSTANCE_CONFIG:
        conf = flask.config.Config('/')
        if isinstance(INSTANCE_CONFIG, dict):
            conf.from_mapping(**INSTANCE_CONFIG)

        else:
            conf.from_pyfile(INSTANCE_CONFIG, silent=False)

    else:
        try:
            conf = flask.current_app.config
        except:
            # Trick to let flask automagically load the config file
            app = flask.Flask('Dummy', instance_path=INSTANCE_PATH, instance_relative_config=True)
            app.config.from_object('config')
            app.config.from_pyfile('config.py')
            conf = app.config
            del app

    return conf


def create_app():
    app = flask.Flask(__name__)
    app.config = get_config()

    for blueprint in ApiFactory().build(app):
        app.register_blueprint(blueprint)

    return app

