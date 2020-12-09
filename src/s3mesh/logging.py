import json


class StructuredMessage:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __str__(self):
        return json.dumps(self.kwargs)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.kwargs == self.kwargs


def json_log(**kwargs) -> StructuredMessage:
    return StructuredMessage(**kwargs)
