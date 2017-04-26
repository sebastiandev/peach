from peach import get_config
from peach.database.proxy import load_db_proxy
from peach.utils import ObjectDict


class BaseModel(ObjectDict):

    type = None
    db = load_db_proxy(get_config()['DATABASE'])

    @property
    def id(self):
        return self._id

    @classmethod
    def build(cls, data):
        raise NotImplementedError()

    @classmethod
    def all(cls):
        for d in cls.db.find(cls, {}):
            yield cls.build(d)

    @classmethod
    def add(cls, doc):
        cls.db.add(cls, doc)

    @classmethod
    def upsert(cls, *docs):
        cls.db.upsert(cls, *docs)

    @classmethod
    def delete(cls, *doc_ids):
        cls.db.delete(cls, *doc_ids)

    @classmethod
    def find(cls, condition, **kwargs):
        return cls.db.find(cls, condition, **kwargs)

    @classmethod
    def by_attr(cls, attr, value, exact=True, many=True, limit=0):
        return cls.db.by_attr(cls, attr, value, exact, many, limit)

    @classmethod
    def by_id(cls, id):
        return cls.db.by_id(cls, id)
