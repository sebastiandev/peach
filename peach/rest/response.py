#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import urllib


class JSONDocumentError(Exception):
    pass


class ResponseDocumentFactory(object):

    @staticmethod
    def data_response(endpoint,
                      request_base_url,
                      request_query_string,
                      data=None,
                      meta=None,
                      links=None,
                      pagination=None,
                      **kwargs):
        return DataDocument(endpoint, request_base_url, request_query_string, data, meta, links, pagination, **kwargs)


class JSONDocument(object):

    def __init__(self, meta=None, links=None, **kwargs):
        self._meta = meta or {}
        self._links = links or {}

    def data(self):
        json_data = {}

        if self._meta:
            json_data['meta'] = self._meta

        if self._links:
            json_data['links'] = self._links

        return json_data


class DataDocument(JSONDocument):

    def __init__(self,
                 endpoint,
                 request_base_url,
                 request_query_string,
                 data=None,
                 meta=None,
                 links=None,
                 pagination=None,
                 **kwargs):
        super().__init__(meta, links, **kwargs)
        self._data = data if data else []

        if pagination:
            self._meta.update(self._build_pagination(pagination))
            self._links.update(self._build_pagination_links(endpoint,
                                                            request_base_url,
                                                            request_query_string,
                                                            pagination))

    def _build_pagination(self, pagination):
        pag_info = {
            'pagination': {
                'total-items': pagination.total,
                'current-page': pagination.page
            }
        }

        if pagination.last is not None:
            pag_info['pagination']['page-count'] = pagination.last + 1

        return pag_info

    def _build_pagination_links(self, endpoint, request_base_url, request_querystring, pagination):
        pagination_links = {}

        def _set_pagination_param(base_url, querystring, page_number):
            page_number_str = pagination.PAGE_NUMBER_ARG.replace('[', '\[').replace(']', '\]')

            if pagination.PAGE_NUMBER_ARG not in querystring:
                querystring += '&{}={}'.format(pagination.PAGE_NUMBER_ARG, page_number)
            else:
                querystring = re.sub('(.*?{})=\d+(.*?)'.format(page_number_str), r'\1' + '={}'.format(str(page_number) + r'\2'),
                             querystring)

            return base_url + '?' + urllib.parse.quote_plus(querystring)

        if 0 < pagination.page:
            pagination_links['first-page'] = _set_pagination_param(request_base_url, request_querystring, 0)
            pagination_links['previous-page'] = _set_pagination_param(request_base_url, request_querystring, pagination.page - 1)

        if pagination.page < pagination.last:
            pagination_links['next-page'] = _set_pagination_param(request_base_url, request_querystring, pagination.page + 1)

        if pagination.page != pagination.last:
            pagination_links['last-page'] = _set_pagination_param(request_base_url, request_querystring, pagination.last)

        return pagination_links

    def add_data(self, data):
        self._data.append(data)

    def data(self):
        json_data = super().data()
        json_data['data'] = self._data
        return json_data
