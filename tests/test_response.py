import pytest
import urllib
from peach.rest.pagination import Pagination
from peach.rest.response import ResponseDocumentFactory


@pytest.mark.parametrize(
    "endpoint, base_url, querystring, data, meta, links, page_size, page_number, total_items",
    [
        (
            'test',                       # endpoint
            '/api/test/',                 # base url
            '',                           # querystring
            [                             # data
                 {
                     'field1': 'xx',
                     'field2': 2
                 }
            ],
            {},                           # meta
            {},                           # links
            None,                         # default page size
            None,                         # default page number
            1                             # total items => should fit in first page, no need for links
        ),
        (
            'test',
            '/api/test/',
            '',
            [],
            {},
            {},
            2,                            # define page size
            None,                         # default page number
            3                             # total items => needs 2 pages
        ),
        (
            'test',
            '/api/test/',
            'filter[name]=foo,var',       # add an existing querystring, should preserve it
            [],
            {},
            {},
            2,                            # define page size
            None,                         # default page number
            3                             # total items => needs 2 pages

        ),
        (
            'test',
            '/api/test/',
            'page[number]=5',            # add an existing querystring with page number, should update the page
            [],
            {},
            {},
            2,                           # define page size
            1,                           # request page 1 (should update querystring replacing the number 5)
            3                            # total items => needs 2 pages
        ),
        (
            'test',
            '/api/test/',
            '',
            [],
            {'some-key': 'xxx'},          # add custom meta
            {},
            25,                           # define page size
            10,                           # request page 10
            300                           # total items => needs 12 pages
        ),

    ]
)
def test_response(endpoint, base_url, querystring, data, meta, links, page_size, page_number, total_items):
    pagination_params = {'total_items': total_items}

    if page_size:
        pagination_params['page_size'] = page_size

    if page_number:
        pagination_params['page_number'] = page_number

    pagination = Pagination(**pagination_params)
    doc = ResponseDocumentFactory.data_response(endpoint, base_url, querystring, data, meta, links, pagination).data()

    if data:
        assert 'data' in doc

    if links:
        assert 'links' in doc

    assert 'meta' in doc

    for k, v in meta.items() or {}.items():
        assert k in doc['meta']
        assert v == doc['meta'][k]

    assert 'pagination' in doc['meta']

    pagination_meta = doc['meta']['pagination']

    assert pagination.total == pagination_meta['total-items']
    assert pagination.page == pagination_meta['current-page']

    if pagination.last is not None:
        assert pagination.last + 1 == pagination_meta['page-count']

    links_data = doc.get('links', {})

    if 0 < pagination.page:
        assert 'first-page' in links_data
        assert 'previous-page' in links_data
        check_pagination_string(links_data['first-page'], base_url, pagination, 0, page_size)
        check_pagination_string(links_data['previous-page'], base_url, pagination, pagination.page - 1, page_size)

    if pagination.page < pagination.last:
        assert 'next-page' in links_data
        check_pagination_string(links_data['next-page'], base_url, pagination, pagination.page + 1, page_size)

    if pagination.page != pagination.last:
        assert 'last-page' in links_data
        check_pagination_string(links_data['last-page'], base_url, pagination, pagination.last, page_size)


def check_pagination_string(pagination_str, base_url, pagination, page_number, page_size):
    assert pagination_str.startswith(base_url + '?')

    new_querystring = pagination_str.replace(base_url + '?', '')
    new_querystring = urllib.parse.unquote_plus(new_querystring)

    pagination_size_str = "{}={}".format(pagination.PAGE_SIZE_ARG, page_size or pagination.DEFAULT_SIZE)
    pagination_number_str = "{}={}".format(pagination.PAGE_NUMBER_ARG, page_number or pagination.DEFAULT_NUMBER)

    assert pagination_size_str in new_querystring
    # Make sure it only appears once
    assert new_querystring.find(pagination_size_str) == new_querystring.rfind(pagination_size_str)

    assert pagination_number_str in new_querystring
    # Make sure it only appears once
    assert new_querystring.find(pagination_number_str) == new_querystring.rfind(pagination_number_str)
