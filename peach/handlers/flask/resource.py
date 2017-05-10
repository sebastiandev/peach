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


class FlaskBaseResource(BaseResource, flask_restful.Resource):

    def __init__(self, *args, **kwargs):
        BaseResource.__init__(self, FlaskRequestHelper(), *args, **kwargs)
        flask_restful.Resource.__init__(self)
        self._request_helper.parse(flask_restful.request, self.REQUEST_ARGS)

    # Need to specify these again because for some reason Flask MethodView doesn't pick up
    # the class methods inherited from BaseResource

    def get(self, ids=None):
        return super().get(ids)

    def post(self):
        return super().post()

    def delete(self, ids=None):
        return super().delete(ids)

    def patch(self, ids=None):
        return super().patch(ids)

    def put(self, ids=None):
        return super().put(ids)
