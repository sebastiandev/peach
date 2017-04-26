#!/usr/bin/python
# -*- coding: utf-8 -*-


class JSONDocumentError(Exception):
    pass


class ResponseFactory(object):

    @staticmethod
    def data_response(data=None, included=None, meta=None):
        return DataDocument(data, included, meta)

    @staticmethod
    def error_response(errors=None):
        return ErrorDocument(errors)


class JSONDocument(object):

    def __init__(self, included=None, meta=None):
        self._included = included if included else []
        self._links = None
        self._meta = meta

    def add_included(self, data):
        self._included.append(data)

    @property
    def links(self):
        return self._links

    @links.setter
    def links(self, data):
        self._links = data

    def data(self):
        json_data = {}

        if self._included:
            json_data['included'] = self._included

        if self._meta:
            json_data['meta'] = self._meta

        if self._links:
            json_data['links'] = self._links

        return json_data


class DataDocument(JSONDocument):

    def __init__(self, data=None, included=None, meta=None):
        super().__init__(included, meta)
        self._data = data if data else []

    def add_data(self, data):
        self._data.append(data)

    def data(self):
        json_data = super().data()
        json_data['data'] = self._data
        return json_data


class ErrorDocument(JSONDocument):

    def __init__(self, errors=None, included=None, links=None):
        super().__init__(included, links)
        self._errors = errors if errors else []

    def add_error(self, serialized_item):
        self._errors.append(serialized_item)

    def data(self):
        json_data = super().data()
        json_data['errors'] = self._errors
        return json_data
