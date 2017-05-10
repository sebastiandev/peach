import json
import re
import falcon
from peach.rest.base_api import ApiFactory, ApiException
from peach.handlers.falcon  import int_to_falcon_status


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
        app.add_error_handler(ApiException, self.handle_error)

    def handle_error(self, ex, req, resp, params):
        resp.body = json.dumps(ex.data)
        resp.status = int_to_falcon_status(ex.status)


