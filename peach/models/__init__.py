from peach import Peach
from peach.database.proxy import load_db_proxy
from peach.utils import ObjectDict


class BaseModel(ObjectDict):

    type = None
    db = load_db_proxy(Peach().database_config)

    @property
    def id(self):
        return self._id

    @classmethod
    def build(cls, data):
        raise NotImplementedError()

    @classmethod
    def count(cls, condition=None, **kwargs):
        return cls.db.count(cls, condition, **kwargs)

    @classmethod
    def all(cls, skip=0, limit=0, sort=None):
        for d in cls.db.find(cls, {}, skip=skip, limit=limit, sort=sort):
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
    def find(cls, condition, skip=0, limit=0, sort=None, **kwargs):
        return cls.db.find(cls, condition, skip=skip, limit=limit, sort=sort, **kwargs)

    @classmethod
    def by_attr(cls, attr, value, exact=True, many=True, skip=0, limit=0, sort=None):
        return cls.db.by_attr(cls, attr, value, exact, many, skip=skip, limit=limit, sort=sort)

    @classmethod
    def by_id(cls, id):
        return cls.db.by_id(cls, id)
