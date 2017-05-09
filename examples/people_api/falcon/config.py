APIS = {
    'api': {
        'prefix': '/api',
        'name': 'People Api',
        'version': '0.0.1',
        'pagination': 'peach.rest.pagination.Pagination',
        'response_factory': 'peach.rest.response.ResponseDocumentFactory',
        'endpoints': [
            {
                'name': 'people',
                'class': 'examples.people_api.falcon.app.PeopleResource',
                'urls': [
                    '/people',
                    '/people/{ids}'
                ]
            }
        ]
    }
}


DATABASE = {
    'proxy': 'peach.database.mongo_proxy.MongoDBProxy',
    'uri': 'mongodb://localhost:27017/',
    'name': 'people_api'
}

