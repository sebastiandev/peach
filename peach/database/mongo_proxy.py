from pymongo import MongoClient
from .proxy import DBProxy


class MongoDBProxy(DBProxy):

    @classmethod
    def build(cls, uri, name, **kwargs):
        return MongoDBProxy(MongoClient(uri)[name])

    def __init__(self, db):
        self._db = db

    def collection(self, model):
        collection_name = model.collection_name or model.__class__.__name__.lower() + 's'
        return self._db[collection_name]

    def add(self, model, doc):
        self.collection(model).insert_one(doc)

    def upsert(self, model, *docs):
        for d in docs:
            self.collection(model).replace_one({'_id': d.id}, d, upsert=True)

    def delete(self, model, *doc_ids):
        for did in doc_ids:
            self.collection(model).delete_one(model, {'_id': did})

    def find(self, model, condition, **kwargs):
        for d in self.collection(model).find(condition, **kwargs):
            yield model.build(d)

    def by_attr(self, model, attr, value, exact=True, many=True, limit=0):
        if exact or type(value) is not str:
            params = {attr: value}
        else:
            params = {attr: {"$regex": '.*?{}.*?'.format(value), "$options": 'si'}}

        if many:
            for d in self.find(model, params, limit=limit):
                yield model.build(d)
        else:
            yield model.build(self.collection(model).find_one(params))

    def by_id(self, model, id):
        return next(self.by_attr(model, '_id', id, many=False))


