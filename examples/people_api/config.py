API_FACTORY = 'peach.rest.api.ApiFactory'

APIS = {
    'api': {
        'prefix': '/api',
        'name': 'People Api',
        'version': '0.0.1',
        'pagination': 'peach.rest.pagination.Pagination',
        'response_factory': 'peach.rest.response.ResponseFactory',
        'endpoints': [
            {
                'name': 'people',
                'class': 'people_api.main.PeopleResource',
                'urls': [
                    '/people',
                    '/people/<string:ids>'
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

