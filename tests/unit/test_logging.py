import json

import pytest
from mock import MagicMock

from s3mesh.logging import JsonFormatter
from tests.builders.common import a_string


def build_log_record(**kwargs):
    record = MagicMock()
    record.levelname = kwargs.get("levelname", a_string())
    record.module = kwargs.get("module", a_string())
    record.msg = kwargs.get("msg", a_string())
    return record


@pytest.mark.parametrize(
    ("json_field", "base_attribute"),
    [("level", "levelname"), ("module", "module"), ("message", "msg")],
)
def test_base_attributes_are_included_in_json(json_field, base_attribute):
    value = a_string()
    record = build_log_record(**{base_attribute: value})
    result = JsonFormatter().format(record)
    assert value == json.loads(result)[json_field]
