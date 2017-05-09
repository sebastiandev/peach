from webargs import fields
from datetime import datetime
from peach.utils import ObjectDict
from .response import ResponseDocumentFactory
from .base_api import ApiException


class InvalidDocumentException(ApiException):
    status = 409


class RequestHelper(object):

    def __init__(self):
        self._req = None
        self._parsed_args = None

    def parse(self, request, supported_args):
        raise NotImplementedError

    @property
    def base_url(self):
        raise NotImplementedError

    @property
    def args(self):
        return self._parsed_args

    @property
    def json(self):
        raise NotImplementedError

    @property
    def querystring(self):
        raise NotImplementedError


class BaseResource(object):

    """
    Note: When defining filters, on the user end, filter names containing underscores
    should be specified converting the underscores to dashes

    Ex:
       If we have a filter named by_name, when hitting the api it should be specified by-name

       >> class ByNameFilter(BaseFilter):
       >>     name = by_name
       >>     value_type = str
       >>     ...

       >> class PeopleResource(BaseResource):
       >>
       >>     model = People
       >>     serializers = [PeopleSerializer]
       >>     filters = [ByNameFilter]
       >>     ...

       >> curl -GET /api/people?filter[by-name]=foo
    """

    model = None
    serializer = None
    filters = []

    SORT_ARG = 'sort'
    FILTER_ARG = 'filter[{}]'

    REQUEST_ARGS = {
        'sort': fields.DelimitedList(fields.Str(), load_from=SORT_ARG, location='query')
    }

    def __init__(self, request_helper, *args, **kwargs):
        self._request_helper = request_helper
        self._api_prefix = kwargs.get('prefix')
        self._db = kwargs.get('database')
        self._pagination_class = kwargs.get('pagination')
        self._response_factory = kwargs.get('response_factory')

        self.REQUEST_ARGS.update(self._pagination_class.REQUEST_ARGS)

        for filter_cls in self.filters:
            filter_user_name = self.FILTER_ARG.format(filter_cls.name.replace('_', '-'))
            self.REQUEST_ARGS[filter_cls.name] = self.filter_value_type_to_request_arg_type(filter_user_name,
                                                                                            filter_cls.value_type,
                                                                                            filter_cls.allow_multiple)

    @staticmethod
    def filter_value_type_to_request_arg_type(name, value_type, allow_multiple, load_from=None):
        if value_type == str:
            arg_type = fields.Str(load_from=load_from or name, location='query')
        elif value_type == float:
            arg_type = fields.Float(load_from=load_from or name, location='query')
        elif value_type == int:
            arg_type = fields.Int(load_from=load_from or name, location='query')
        elif value_type == datetime:
            arg_type = fields.DateTime(load_from=load_from or name, location='query')
        else:
            raise Exception("Unsupported value type '{}' for a request argument".format(value_type))

        if allow_multiple:
            arg_type = fields.DelimitedList(arg_type, load_from=load_from or name, location='query')

        return arg_type

    @property
    def pagination(self):
        return self._pagination_class.from_request_args(self._request_helper.args)

    @property
    def sort_param(self):
        return self._request_helper.args.get('sort')

    @property
    def requested_filters(self):
        filters_by_name = {f.name: f for f in self.filters}

        return ObjectDict(**{
            k: ObjectDict(**{
                'filter_cls': filters_by_name[k],
                'value': v
            }) for k, v in self._request_helper.args.items() if k in filters_by_name and v})

    def build_response(self, data, meta=None, pagination=None):
        endpoint = self._request_helper.base_url.replace(self._api_prefix, '')
        return ResponseDocumentFactory.data_response(endpoint,
                                                     self._request_helper.base_url,
                                                     self._request_helper.querystring,
                                                     data=data,
                                                     meta=meta,
                                                     pagination=pagination)

    def get(self, ids=None):
        meta = {}
        pagination = self.pagination
        filters = self.requested_filters

        if ids:
            data = self.get_by_ids(ids)

        elif filters:
            data, total_count = self.get_by_filters(filters, pagination)
            pagination.total = total_count
            data, errors = self.serializer.serialize(data, many=True)

        else:
            data = self.get_all(pagination)
            pagination.total = self.get_all_count()

        data, errors = self.serializer.serialize(data, many=True)

        return self.build_response(data=data, meta=meta, pagination=pagination).data()

    def get_by_ids(self, ids):
        return list(self.model.by_id(ids[0]))

    def get_all(self, pagination):
        return list(self.model.all(
            sort=self.sort_param,
            skip=pagination.page * pagination.size,
            limit=pagination.size))

    def get_all_count(self):
        return self.model.count()

    def get_by_filters(self, filters, pagination):
        """
        Gets all the entries that satisfy the specified filters. If multiple filters are defined,
        then only those entries that satisfy every single filter will be retrieved. In order words
        multiple filters are combined as an AND concatenation

        :param filters: dict containing the specified filters
        :param pagination: pagination object
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
                                        skip=pagination.page * pagination.size,
                                        limit=pagination.size))

        else:
            filter_def = list(filters.values())[0]
            filter_class = filter_def.filter_cls

            if filter_class.allow_multiple:
                total_count = filter_class.count(self.model, *filter_def.value)
                data = list(filter_class.apply(self.model,
                                               *filter_def.value,
                                               sort=self.sort_param,
                                               skip=pagination.page * pagination.size,
                                               limit=pagination.size))

            else:
                total_count = filter_class.count(self.model, filter_def.value)
                data = list(filter_class.apply(self.model,
                                               filter_def.value,
                                               sort=self.sort_param,
                                               skip=pagination.page * pagination.size,
                                               limit=pagination.size))

        return data, total_count

    def post(self):
        new_item, errors = self.serializer.deserialize(self._request_helper.json)
        if errors:
            raise InvalidDocumentException(title="Invalid document", detail=errors)

        self.model.add(new_item)
        return {}, 201

    def delete(self, ids):
        self.model.delete(*ids.split(','))
        return {}, 204


