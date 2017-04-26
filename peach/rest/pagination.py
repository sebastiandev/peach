# -*- coding: utf-8 -*-
from webargs import fields
from math import ceil


class Pagination(object):

    DEFAULT_NUMBER = 0
    DEFAULT_SIZE = 24

    PAGE_NUMBER_ARG = 'page[number]'
    PAGE_SIZE_ARG = 'page[size]'

    REQUEST_ARGS = {
        'page_number': fields.Int(load_from=PAGE_NUMBER_ARG),
        'page_size': fields.Int(load_from=PAGE_SIZE_ARG),
    }

    def __init__(self, page_number=DEFAULT_NUMBER, page_size=DEFAULT_SIZE, total_items=None, resource=None, params=None):
        self._total_items = total_items
        self._page_number = page_number
        self._page_size = page_size
        self._params = params
        self._resource = resource
        self._last_page = self._calculate_last_result_page(self._total_items, self._page_size)

    @classmethod
    def from_request_args(cls, req_args):
        return Pagination(page_number=req_args.get('page_number', cls.DEFAULT_NUMBER),
                          page_size=req_args.get('page_size', cls.DEFAULT_SIZE))

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, val):
        self._params = val

    @property
    def resource(self):
        return self._resource

    @resource.setter
    def resource(self, val):
        self._resource = val

    @property
    def page(self):
        return self._page_number if self._page_number >= 0 else 0

    @property
    def size(self):
        return self._page_size

    @property
    def last(self):
        return self._last_page

    @last.setter
    def last(self, val):
        self._last_page = val

    @property
    def total(self):
        return self._total_items

    @total.setter
    def total(self, val):
        self._total_items = val
        self._last_page = self._calculate_last_result_page(self._total_items, self._page_size)

    @classmethod
    def _calculate_last_result_page(cls, total_results, page_size):
        if total_results is None:
            last = None
        elif total_results <= page_size:
            last = 0
        else:
            last = int(ceil(float(total_results) / page_size - 1))

        return last
