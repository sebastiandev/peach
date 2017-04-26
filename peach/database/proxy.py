from peach.utils import load_resource_class


def load_db_proxy(db_conf):
    db_proxy_class = load_resource_class(db_conf['proxy'])
    return db_proxy_class.build(**db_conf)


class DBProxy(object):

    @classmethod
    def build(cls, **kwargs):
        raise NotImplementedError

    def add(self, model, doc):
        raise NotImplementedError

    def upsert(self, model, *docs):
        raise NotImplementedError

    def delete(self, model, *doc_ids):
        raise NotImplementedError

    def find(self, model, condition, **kwargs):
        raise NotImplementedError

    def all(self, model):
        raise NotImplementedError

    def by_attr(self, model, attr, value, exact=True, many=True, limit=0):
        raise NotImplementedError

    def by_id(self, model, id):
        raise NotImplementedError
