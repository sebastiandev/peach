from peach.database.proxy import load_db_proxy
from peach.utils import load_resource_class, ObjectDict
from peach.rest.pagination import Pagination
from peach.rest.response import ResponseDocumentFactory


class ApiFactory(object):

    @classmethod
    def load_api_resource_params(cls, app_conf, api_conf):
        db_conf = app_conf.get('DATABASE')
        pagination_class = load_resource_class(api_conf.get('pagination')) or Pagination
        response_factory = load_resource_class(api_conf.get('response_factory')) or ResponseDocumentFactory

        return ObjectDict(**{
            'prefix': api_conf.get('prefix'),
            'database': load_db_proxy(db_conf),
            'pagination': pagination_class,
            'response_factory': response_factory
        })

    def _api_definitions(self, app_conf):
        definitions = ObjectDict()

        for api_id, api_def in iter(app_conf.get('APIS', {}).items()):
            definitions[api_id] = ObjectDict(**{
                'name': api_def.get('name', api_id).title(),
                'prefix': api_def.get('prefix'),
                'version': api_def.get('version'),
                'mediatype': api_def.get('mediatype'),
                'conf': app_conf,
                'endpoints': ObjectDict()
            })

            for endpoint in api_def.get('endpoints', []):
                definitions[api_id]['endpoints'][endpoint['name']] = ObjectDict(**{
                    'handler': load_resource_class(endpoint['class']),
                    'urls': endpoint['urls'],
                    'name': endpoint['name'],
                    'params': self.load_api_resource_params(app_conf, api_def)
                })

            return definitions

    def _build_api(self, app, api_def):
        raise NotImplementedError

    def build(self, app, config=None):
        return [self._build_api(app, api_def) for api_def in self._api_definitions(config or getattr(app, 'config')).values()]


class ApiException(Exception):

    GET = 'get'
    POST = 'post'
    PATCH = 'patch'
    DELETE = 'delete'

    status = None

    def __init__(self, title, detail):
        self.title = title
        self.detail = detail

    @property
    def data(self):
        return {
            'status': self.status,
            'detail': self.detail,
            'title': self.title,
            'meta': self.meta if hasattr(self, 'meta') else {}
        }
