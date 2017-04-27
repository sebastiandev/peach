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

    def count(self, model, condition, **kwargs):
        raise NotImplementedError

    def find(self, model, condition, skip=0, limit=0, sort=None, **kwargs):
        raise NotImplementedError

    def by_attr(self, model, attr, value, exact=True, many=True, skip=0, limit=0, sort=None):
        raise NotImplementedError

    def by_id(self, model, id):
        raise NotImplementedError
