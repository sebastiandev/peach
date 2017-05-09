import urllib
import flask_restful
from webargs.flaskparser import parser as req_parser
from peach.utils import ObjectDict
from peach.rest.resource import BaseResource, RequestHelper


class FlaskRequestHelper(RequestHelper):

    def parse(self, request, supported_args):
        self._req = request
        self._parsed_args = ObjectDict(**req_parser.parse(supported_args))

    @property
    def base_url(self):
        return self._req.base_url

    @property
    def json(self):
        return self._req.json

    @property
    def querystring(self):
        return urllib.parse.unquote_plus(self._req.query_string.decode())


class FlaskBaseResource(flask_restful.Resource, BaseResource):

    def __init__(self, *args, **kwargs):
        flask_restful.Resource.__init__(self)
        BaseResource.__init__(self, FlaskRequestHelper(), *args, **kwargs)
        self._request_helper.parse(flask_restful.request, self.REQUEST_ARGS)
