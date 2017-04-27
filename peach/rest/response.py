#!/usr/bin/python
# -*- coding: utf-8 -*-


class JSONDocumentError(Exception):
    pass


class ResponseFactory(object):

    @staticmethod
    def data_response(data=None, meta=None, pagination=None, **kwargs):
        return DataDocument(data, meta, pagination, **kwargs)


class JSONDocument(object):

    def __init__(self, meta=None, **kwargs):
        self._meta = meta or {}

    def data(self):
        json_data = {}

        if self._meta:
            json_data['meta'] = self._meta

        return json_data


class DataDocument(JSONDocument):

    def __init__(self, data=None, meta=None, pagination=None, **kwargs):
        super().__init__(meta, **kwargs)
        self._data = data if data else []

        if pagination:
            self._build_pagination(pagination)

    def _build_pagination(self, pagination):
        pag_info = {
            'pagination': {
                'total-items': pagination.total,
                'current-page': pagination.page
            }
        }

        if pagination.last is not None:
            pag_info['pagination']['page-count'] = pagination.last + 1

        self._meta.update(pag_info)

    def add_data(self, data):
        self._data.append(data)

    def data(self):
        json_data = super().data()
        json_data['data'] = self._data
        return json_data
