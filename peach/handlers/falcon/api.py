import json
import re
import falcon
from peach.rest.base_api import ApiFactory, ApiException


class FalconApiFactory(ApiFactory):

    def _build_api(self, app, api_def):
        prefix = api_def.prefix.replace('/', '')
        api_route = "/{}".format(prefix)

        rest_api = FalconRestApi(app=app,
                                 prefix=prefix,
                                 name=api_def.name,
                                 version=api_def.version,
                                 media_type=api_def.mediatype)

        for name, endpoint in api_def.endpoints.items():
            for url in endpoint.urls:
                endpoint_url = re.sub(r'/+', '/', "{}/{}".format(api_route, url))
                app.add_route(endpoint_url, endpoint.handler(**endpoint.params))

        return rest_api


class FalconRestApi(object):

    MEDIA_TYPE = 'application/json'
    DEFAULT_HEADER = {'Content-Type': MEDIA_TYPE}

    def __init__(self,
                 app,
                 prefix,
                 name=None,
                 version=None,
                 media_type=None,
                 **kwargs):
        self._media_type = media_type or self.MEDIA_TYPE

        class EntryPoint(object):

            def on_get(self, req, resp):
                resp.body = json.dumps({
                    'name': name or 'Peach Rest Api',
                    'version': version or '0.0.0',
                })
                resp.status = falcon.HTTP_200

        app._media_type = self._media_type
        app.add_route('/{}'.format(prefix), EntryPoint())

    # def handle_error(self, e):
    #     if isinstance(e, ApiException):
    #         error_response = make_response(jsonify(e.data), e.status)
    #         error_response = '{}' if e.status == 200 else error_response
    #
    #     else:
    #         error_response = super().handle_error(e)
    #
    #     return error_response

