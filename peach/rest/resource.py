import urllib
from flask_restful import Resource, request
from webargs import fields
from webargs.flaskparser import parser as req_parser
from datetime import datetime
from peach.utils import ObjectDict
from .response import ResponseFactory


class BaseResource(Resource):

    model = None
    serializer = None

    SORT_ARG = 'sort'

    REQUEST_ARGS = {
        'sort': fields.DelimitedList(fields.Str(), load_from=SORT_ARG)
    }

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._base_url = request.base_url
        self._api_url = request.url_root + kwargs.get('prefix').replace('/', '')
        self._db = kwargs.get('database')
        self._pagination_class = kwargs.get('pagination')
        self._response_factory = kwargs.get('response_factory')

        self.REQUEST_ARGS.update(self._pagination_class.REQUEST_ARGS)
        self._args = ObjectDict(**req_parser.parse(self.REQUEST_ARGS, request))

        self.pagination = self._pagination_class.from_request_args(self._args)

    def base_url_without_params(self, params):
        return self._base_url.replace('/' + params, '')

    @property
    def json_request(self):
        return request.json

    @property
    def api_endpoint(self):
        return self._base_url.replace(self._api_url, '')

    @property
    def url_query_string(self):
        return urllib.parse.unquote_plus(request.query_string)

    @property
    def sort_param(self):
        return self._args.get('sort')

    def build_response(self, data, meta=None):
        return ResponseFactory.data_response(data=data, meta=meta, pagination=self.pagination)

    def get(self, ids=None):
        meta = {}

        if ids:
            data = self.get_by_ids(ids)

        else:
            data = self.get_all()
            self.pagination.total = self.get_all_count()

        data, errors = self.serializer.serialize(data, many=True)

        return self.build_response(data=data, meta=meta).data()

    def get_by_ids(self, ids):
        return list(self.model.by_id(ids[0]))

    def get_all(self):
        return list(self.model.all(
            sort=self.sort_param,
            skip=self.pagination.page * self.pagination.size,
            limit=self.pagination.size))

    def get_all_count(self):
        return self.model.count()

    def post(self):
        new_item, errors = self.serializer.deserialize(self.json_request)
        self.model.add(new_item)
        return {}, 201

    def delete(self, ids):
        self.model.delete(*ids.split(','))
        return {}, 204


class FiltrableResource(BaseResource):

    """
    An extended resource that enables result filtering by using model filters

    Note: When defining filters, on the user end, filter names containing underscores
    should be specified converting the underscores to dashes

    Ex:
       If we have a filter named by_name, when hitting the api it should be specified by-name

       >> class ByNameFilter(BaseFilter):
       >>     name = by_name
       >>     value_type = str
       >>     ...

       >> class PeopleResource(FiltrableResource):
       >>     filters = [ByNameFilter]
       >>     ...

       >> curl -GET /api/people?filter[by-name]=foo

    """
    FILTER_ARG = 'filter[{}]'
    filters = []

    @staticmethod
    def filter_value_type_to_request_arg_type(name, value_type, allow_multiple, load_from=None):
        if value_type == str:
            arg_type = fields.Str(load_from=load_from or name)
        elif value_type == float:
            arg_type = fields.Float(load_from=load_from or name)
        elif value_type == int:
            arg_type = fields.Int(load_from=load_from or name)
        elif value_type == datetime:
            arg_type = fields.DateTime(load_from=load_from or name)
        else:
            raise Exception("Unsupported value type '{}' for a request argument".format(value_type))

        if allow_multiple:
            arg_type = fields.DelimitedList(arg_type, load_from=load_from or name)

        return arg_type

    def __init__(self, *args, **kwargs):
        for filter_cls in self.filters:
            filter_user_name = self.FILTER_ARG.format(filter_cls.name.replace('_', '-'))
            self.REQUEST_ARGS[filter_cls.name] = self.filter_value_type_to_request_arg_type(filter_user_name,
                                                                                            filter_cls.value_type,
                                                                                            filter_cls.allow_multiple)

        super().__init__(*args, **kwargs)

    @property
    def requested_filters(self):
        filters_by_name = {f.name: f for f in self.filters}

        return ObjectDict(**{
            k: ObjectDict(**{
                'filter_cls': filters_by_name[k],
                'value': v
            }) for k, v in self._args.items() if k in filters_by_name and v})

    def get(self, ids=None):
        meta = {}
        filters = self.requested_filters

        if filters:
            data, total_count = self.get_by_filters(filters)
            self.pagination.total = total_count
            data, errors = self.serializer.serialize(data, many=True)
            response = self.build_response(data=data, meta=meta).data()

        else:
            response = super().get(ids)

        return response

    def get_by_filters(self, filters):
        """
        Gets all the entries that satisfy the specified filters. If multiple filters are defined,
        then only those entries that satisfy every single filter will be retrieved. In order words
        multiple filters are combined as an AND concatenation

        :param filters: dict containing the specified filters
        :return: filtered result
        """
        if len(filters) > 1:
            condition = {}
            for filter_def in filters.values():
                filter_class = filter_def.filter_cls

                if filter_class.allow_multiple:
                    condition.update(filter_class.condition(*filter_def.value))

                else:
                    condition.update(filter_class.condition(filter_def.value))

            total_count = self.model.count(condition)
            data = list(self.model.find(condition,
                                        sort=self.sort_param,
                                        skip=self.pagination.page * self.pagination.size,
                                        limit=self.pagination.size))

        else:
            filter_def = list(filters.values())[0]
            filter_class = filter_def.filter_cls

            if filter_class.allow_multiple:
                total_count = filter_class.count(self.model, *filter_def.value)
                data = list(filter_class.apply(self.model,
                                               *filter_def.value,
                                               sort=self.sort_param,
                                               skip=self.pagination.page * self.pagination.size,
                                               limit=self.pagination.size))

            else:
                total_count = filter_class.count(self.model, filter_def.value)
                data = list(filter_class.apply(self.model,
                                               filter_def.value,
                                               sort=self.sort_param,
                                               skip=self.pagination.page * self.pagination.size,
                                               limit=self.pagination.size))

        return data, total_count


