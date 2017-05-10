import urllib
import json
from webargs.falconparser import parser as req_parser
from peach.utils import ObjectDict
from peach.rest.resource import BaseResource, RequestHelper
from peach.handlers.falcon import int_to_falcon_status


class FalconRequestHelper(RequestHelper):

    def parse(self, request, supported_args):
        self._req = request

        try:
            self._json = json.load(self._req.bounded_stream)
        except:
            self._json = {}

        self._parsed_args = ObjectDict(**req_parser.parse(supported_args, self._req))

    @property
    def base_url(self):
        return self._req.path

    @property
    def json(self):
        return self._json

    @property
    def querystring(self):
        return urllib.parse.unquote_plus(self._req.query_string)


def handle_req_and_resp(f):
    def wrapped_f(instance, req, resp, **kwargs):
        # Parses the request to make data available for the resource
        instance._request_helper.parse(req, instance.REQUEST_ARGS)
        data, status = f(instance, req, resp, **kwargs)

        # Builds the response as expected by falcon
        resp.body = json.dumps(data)
        resp.status = int_to_falcon_status(status)

    return wrapped_f


class FalconBaseResource(BaseResource):

    def __init__(self, *args, **kwargs):
        super().__init__(FalconRequestHelper(), *args, **kwargs)

    @handle_req_and_resp
    def on_get(self, req, resp, **kwargs):
        return self.get(**kwargs)

    @handle_req_and_resp
    def on_post(self, req, resp, **kwargs):
        return self.post()

    @handle_req_and_resp
    def on_put(self, req, resp, **kwargs):
        return self.put(**kwargs)

    @handle_req_and_resp
    def on_delete(self, req, resp, **kwargs):
        return self.delete(**kwargs)

    @handle_req_and_resp
    def on_patch(self, req, resp, **kwargs):
        return self.patch(**kwargs)
