

class BaseFilter(object):

    name = None
    value_type = None
    allow_multiple = None

    @classmethod
    def condition(cls, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def apply(cls, model, *args, **kwargs):
        return model.find(cls.condition(*args, **kwargs), limit=kwargs.get('limit', 0))




