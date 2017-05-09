import urllib
import falcon
import json
from webargs.falconparser import parser as req_parser
from peach.utils import ObjectDict
from peach.rest.resource import BaseResource, RequestHelper


class FalconRequestHelper(RequestHelper):

    def parse(self, request, supported_args):
        self._req = request
        self._parsed_args = ObjectDict(**req_parser.parse(supported_args, self._req))

    @property
    def base_url(self):
        return self._req.path

    @property
    def json(self):
        return json.load(self._req.bounded_stream)

    @property
    def querystring(self):
        return urllib.parse.unquote_plus(self._req.query_string)


class FalconBaseResource(BaseResource):

    def __init__(self, *args, **kwargs):
        super().__init__(FalconRequestHelper(), *args, **kwargs)

    def on_get(self, req, resp, **kwargs):
        self._request_helper.parse(req, self.REQUEST_ARGS)
        data = self.get(**kwargs)
        resp.body = json.dumps(data)
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp, **kwargs):
        self._request_helper.parse(req, self.REQUEST_ARGS)
        data, status = self.post()
        resp.body = json.dumps(data)
        resp.status = status

    def on_put(self, req, resp, **kwargs):
        self._request_helper.parse(req, self.REQUEST_ARGS)
        data, status = self.put(**kwargs)
        resp.body = json.dumps(data)
        resp.status = status

    def on_delete(self, req, resp, **kwargs):
        self._request_helper.parse(req, self.REQUEST_ARGS)
        data, status = self.delete(**kwargs)
        resp.body = json.dumps(data)
        resp.status = status
