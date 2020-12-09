import logging
import json

from unittest import mock

from s3mesh.logging import json_log, StructuredMessage

def test_log_calls_logging_with_json():
     values = dict(foo='bar', bar='baz', num=123, fnum=123.456)
     message = json_log(**values)
     assert message == StructuredMessage(**values)
