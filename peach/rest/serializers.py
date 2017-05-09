from marshmallow import Schema, fields, post_load


class ModelSerializer(Schema):

    model = None

    @classmethod
    def serialize(cls, data, filters=None, many=False):
        ser_params = {'many': many}
        if filters:
            ser_params['only'] = tuple(f for f in filters)

        serialization = cls(**ser_params).dump(data)
        return serialization.data, serialization.errors

    @classmethod
    def deserialize(cls, data):
        deserialization = cls().load(data)
        return deserialization.data, deserialization.errors

    @post_load
    def build(self, data):
        return self.model.build(data)
