from s3mesh.logging import StructuredMessage, json_log


def test_log_calls_logging_with_json():
    values = {"foo": "bar", "bar": "baz", "num": 123, "fnum": 123.456}
    message = json_log(**values)
    assert message == StructuredMessage(**values)
