

class BaseFilter(object):

    name = None
    value_type = None
    allow_multiple = None

    @classmethod
    def condition(cls, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def apply(cls, model, *args, **kwargs):
        return model.find(cls.condition(*args, **kwargs),
                          skip=kwargs.get('skip', 0),
                          limit=kwargs.get('limit', 0))

    @classmethod
    def count(cls, model, *args, **kwargs):
        return model.count(cls.condition(*args, **kwargs))



