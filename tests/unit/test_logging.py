import json

import pytest
from mock import MagicMock

from s3mesh.logging import JsonFormatter
from tests.builders.common import a_string
from tests.builders.mesh import an_epoch_timestamp


def build_log_record(**kwargs):
    record = MagicMock()
    record.levelname = kwargs.get("levelname", a_string())
    record.module = kwargs.get("module", a_string())
    record.msg = kwargs.get("msg", a_string())
    record.created = kwargs.get("created", an_epoch_timestamp())
    return record


@pytest.mark.parametrize(
    ("json_field", "base_attribute"),
    [("level", "levelname"), ("module", "module"), ("message", "msg")],
)
def test_base_attributes_are_included_in_json(json_field, base_attribute):
    value = a_string()
    record = build_log_record(**{base_attribute: value})

    actual_json_string = JsonFormatter().format(record)
    actual = json.loads(actual_json_string)[json_field]

    assert value == actual


def test_timestamp_is_included_in_json():
    record = build_log_record(created=1607965513.358049)
    actual_json_string = JsonFormatter().format(record)
    actual = json.loads(actual_json_string)["time"]

    expected = "2020-12-14T17:05:13.358049"

    assert actual == expected
