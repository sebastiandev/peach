

class BaseFilter(object):

    name = None
    value_type = None
    allow_multiple = None

    @classmethod
    def condition(cls, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def apply(cls, model, *args, **kwargs):
        sort = kwargs.pop('sort', None)
        skip = kwargs.pop('skip', None)
        limit = kwargs.pop('limit', None)

        return model.find(cls.condition(*args, **kwargs), skip=skip, limit=limit, sort=sort)

    @classmethod
    def count(cls, model, *args, **kwargs):
        kwargs.pop('sort', None)
        kwargs.pop('skip', None)
        kwargs.pop('limit', None)
        return model.count(cls.condition(*args, **kwargs))



