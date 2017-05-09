import flask_restful
from flask import Blueprint, jsonify, make_response
from peach.rest.base_api import ApiFactory, ApiException


class FlaskApiFactory(ApiFactory):

    def _build_api(self, app, api_def):
        api_blueprint = Blueprint(api_def.name, api_def.name, url_prefix=api_def.prefix)
        api_blueprint.conf = api_def.conf

        rest_api = FlaskRestApi(app=api_blueprint,
                                name=api_def.name,
                                version=api_def.version,
                                media_type=api_def.mediatype)

        for name, endpoint in api_def.endpoints.items():
            rest_api.add_resource(endpoint.handler,
                                  *endpoint.urls,
                                  endpoint=name,
                                  resource_class_kwargs=endpoint.params)

        return api_blueprint


class FlaskRestApi(flask_restful.Api):

    MEDIA_TYPE = 'application/json'
    DEFAULT_HEADER = {'Content-Type': MEDIA_TYPE}

    def __init__(self,
                 app,
                 name=None,
                 version=None,
                 media_type=None,
                 **kwargs):
        super().__init__(app=app, default_mediatype=media_type or self.MEDIA_TYPE, **kwargs)

        @app.route('/')
        def main():
            return jsonify({
                'name': name or 'Peach Rest Api',
                'version': version or '0.0.0',
            })

    def handle_error(self, e):
        if isinstance(e, ApiException):
            error_response = make_response(jsonify(e.data), e.status)
            error_response = '{}' if e.status == 200 else error_response

        else:
            error_response = super().handle_error(e)

        return error_response

