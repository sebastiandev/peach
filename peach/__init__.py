import flask
from peach.rest.api import ApiFactory

INSTANCE_PATH = None


def get_config():
    try:
        conf = flask.current_app.config
    except:
        app = flask.Flask('temp app for context', instance_path=INSTANCE_PATH, instance_relative_config=True)
        app.config.from_object('config')
        app.config.from_pyfile('config.py')
        conf = app.config
        del app

    return conf


def create_app():
    app = flask.Flask(__name__, instance_path=INSTANCE_PATH, instance_relative_config=True)
    app.config.from_object('config')
    app.config.from_pyfile('config.py')

    for blueprint in ApiFactory().build(app):
        app.register_blueprint(blueprint)

    return app

