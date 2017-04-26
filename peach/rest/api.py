import flask_restful
from flask import Blueprint, jsonify
from peach.database.proxy import load_db_proxy
from peach.utils import load_resource_class, ObjectDict


class Conf(ObjectDict):
    pass


class ApiFactory(object):

    @classmethod
    def load_conf(cls, app):
        db_conf = app.config.get('DATABASE')

        return Conf(**{
            'database': load_db_proxy(db_conf)
        })

    @classmethod
    def build(cls, app):
        blueprints = []
        apis_definitions = app.config.get('APIS', [])

        for api_id, api_def in iter(apis_definitions.items()):
            api_name = api_def.get('name', api_id).title()
            api_url_prefix = api_def.get('prefix')
            api_version = api_def.get('version')
            api_media_type = api_def.get('mediatype')

            api_blueprint = Blueprint(api_name, api_id, url_prefix=api_url_prefix)
            api_blueprint.conf = cls.load_conf(app)

            rest_api = RestApi(app=api_blueprint, name=api_name, version=api_version, media_type=api_media_type)

            for endpoint in api_def.get('endpoints', []):
                rest_api.add_resource(load_resource_class(endpoint['class']),
                                      *endpoint['urls'],
                                      endpoint=endpoint['name'],
                                      resource_class_kwargs=api_blueprint.conf)

            blueprints.append(api_blueprint)

        return blueprints


class ApiException(Exception):

    GET = 'get'
    POST = 'post'
    PATCH = 'patch'
    DELETE = 'delete'

    @property
    def data(self):
        return {
            'status': self.status,
            'detail': self.detail,
            'title': self.title,
            'meta': self.meta if hasattr(self, 'meta') else {}
        }


class RestApi(flask_restful.Api):

    MEDIA_TYPE = 'application/json'
    DEFAULT_HEADER = {'Content-Type': MEDIA_TYPE}

    def __init__(self,
                 app,
                 name=None,
                 version=None,
                 prefix=None,
                 media_type=MEDIA_TYPE,
                 errors=None,
                 decorators=None):
        super().__init__(app=app,
                         prefix=prefix,
                         default_mediatype=media_type or self.MEDIA_TYPE,
                         decorators=decorators,
                         errors=errors)

        @app.route('/')
        def main():
            return jsonify({
                'name': name,
                'version': version or '0.0.0',
            })

    def handle_error(self, e):
        if isinstance(e, ApiException):
            error_response = self.output_json(e.data, e.status)
            error_response = '{}' if e.status == 200 else error_response

        else:
            error_response = super().handle_error(e)

        return error_response
