import logging
from unittest import mock
from unittest.mock import MagicMock, call, patch

import pytest

from s3mesh.forwarder import MeshToS3Forwarder
from s3mesh.mesh import InvalidMeshHeader, MissingMeshHeader
from tests.builders.common import a_string


def _an_invalid_header_exception(**kwargs):
    return InvalidMeshHeader(
        header_name=kwargs.get("header_name", a_string()),
        header_value=kwargs.get("header_value", a_string()),
        expected_header_value=kwargs.get("expected_header_value", a_string()),
    )


def _a_missing_header_exception(**kwargs):
    return MissingMeshHeader(
        header_name=kwargs.get("header_name", a_string()),
    )


def test_validates_message():
    mock_mesh_inbox = MagicMock()
    mock_s3_uploader = MagicMock()
    mock_mesh_message = MagicMock()
    mock_mesh_inbox.read_messages.return_value = iter([mock_mesh_message])
    forwarder = MeshToS3Forwarder(mock_mesh_inbox, mock_s3_uploader)

    forwarder.forward_messages()

    mock_mesh_message.validate.assert_called_once()


def test_forwards_message():
    mock_mesh_inbox = MagicMock()
    mock_s3_uploader = MagicMock()
    mock_mesh_message = MagicMock()
    mock_mesh_inbox.read_messages.return_value = iter([mock_mesh_message])
    forwarder = MeshToS3Forwarder(mock_mesh_inbox, mock_s3_uploader)

    forwarder.forward_messages()

    mock_s3_uploader.upload.assert_called_once_with(mock_mesh_message)


def test_acknowledges_message():
    mock_mesh_inbox = MagicMock()
    mock_s3_uploader = MagicMock()
    mock_mesh_message = MagicMock()
    mock_mesh_inbox.read_messages.return_value = iter([mock_mesh_message])
    forwarder = MeshToS3Forwarder(mock_mesh_inbox, mock_s3_uploader)

    forwarder.forward_messages()

    mock_mesh_message.acknowledge.assert_called_once()


def test_forwards_multiple_messages():
    mock_mesh_inbox = MagicMock()
    mock_s3_uploader = MagicMock()
    mock_mesh_message_one = MagicMock()
    mock_mesh_message_two = MagicMock()
    mock_mesh_messages = [mock_mesh_message_one, mock_mesh_message_two]
    mock_mesh_inbox.read_messages.return_value = iter(mock_mesh_messages)
    forwarder = MeshToS3Forwarder(mock_mesh_inbox, mock_s3_uploader)

    forwarder.forward_messages()

    mock_s3_uploader.upload.assert_has_calls(
        [
            call(mock_mesh_message_one),
            call(mock_mesh_message_two),
        ]
    )

    assert mock_s3_uploader.upload.call_count == 2


def test_acknowledges_multiple_message():
    mock_mesh_inbox = MagicMock()
    mock_s3_uploader = MagicMock()
    mock_mesh_messages = [MagicMock(), MagicMock()]
    mock_mesh_inbox.read_messages.return_value = iter(mock_mesh_messages)
    forwarder = MeshToS3Forwarder(mock_mesh_inbox, mock_s3_uploader)

    forwarder.forward_messages()

    for mock_mesh_message in mock_mesh_messages:
        mock_mesh_message.acknowledge.assert_called_once()


def test_logs_message_progress():
    logger = logging.getLogger("s3mesh.forwarder")

    mock_mesh_inbox = MagicMock()
    mock_s3_uploader = MagicMock()
    mock_mesh_message = MagicMock()
    mock_mesh_message.id = "123"
    mock_mesh_message.file_name = "a_file.dat"
    mock_mesh_inbox.read_messages.return_value = iter([mock_mesh_message])
    forwarder = MeshToS3Forwarder(mock_mesh_inbox, mock_s3_uploader)

    with patch.object(logger, "info") as mock_info:
        forwarder.forward_messages()

    mock_info.assert_has_calls(
        [
            call("Message received", extra={"messageId": "123", "fileName": "a_file.dat"}),
            call("Message uploaded", extra={"messageId": "123"}),
            call("Message acknowledged", extra={"messageId": "123"}),
        ],
        any_order=False,
    )


def test_catches_invalid_header_error():
    mock_mesh_inbox = MagicMock()
    mock_s3_uploader = MagicMock()
    mock_mesh_message = MagicMock()
    mock_mesh_inbox.read_messages.return_value = iter([mock_mesh_message])
    forwarder = MeshToS3Forwarder(mock_mesh_inbox, mock_s3_uploader)
    mock_mesh_message.validate.side_effect = _an_invalid_header_exception()

    try:
        forwarder.forward_messages()
    except InvalidMeshHeader:
        pytest.fail("InvalidMeshHeader was raised when it shouldn't have been")


def test_calls_logger_with_a_warning_when_message_has_invalid_header():
    mock_mesh_inbox = MagicMock()
    mock_s3_uploader = MagicMock()
    mock_mesh_message = MagicMock()
    mock_mesh_message.id = "abc"

    mock_mesh_inbox.read_messages.return_value = iter([mock_mesh_message])
    forwarder = MeshToS3Forwarder(mock_mesh_inbox, mock_s3_uploader)
    mock_mesh_message.validate.side_effect = _an_invalid_header_exception(
        header_name="fruit_header",
        header_value="banana",
        expected_header_value="mango",
    )
    logger = logging.getLogger("s3mesh.forwarder")

    with mock.patch.object(logger, "warning") as mock_warn:
        forwarder.forward_messages()

    mock_warn.assert_called_with(
        "Message abc: " "Invalid MESH fruit_header header - expected: mango, " "instead got: banana"
    )


def test_continues_uploading_messages_when_one_of_them_has_invalid_mesh_header():
    mock_mesh_inbox = MagicMock()
    mock_s3_uploader = MagicMock()
    successful_message_1 = MagicMock()
    successful_message_2 = MagicMock()
    unsuccessful_message = MagicMock()
    unsuccessful_message.validate.side_effect = _an_invalid_header_exception()

    mock_mesh_inbox.read_messages.return_value = iter(
        [successful_message_1, unsuccessful_message, successful_message_2]
    )

    forwarder = MeshToS3Forwarder(mock_mesh_inbox, mock_s3_uploader)

    forwarder.forward_messages()

    mock_s3_uploader.upload.assert_has_calls(
        [
            call(successful_message_1),
            call(successful_message_2),
        ]
    )


def test_catches_missing_header_error():
    mock_mesh_inbox = MagicMock()
    mock_s3_uploader = MagicMock()
    mock_mesh_message = MagicMock()
    mock_mesh_inbox.read_messages.return_value = iter([mock_mesh_message])
    forwarder = MeshToS3Forwarder(mock_mesh_inbox, mock_s3_uploader)
    mock_mesh_message.validate.side_effect = _a_missing_header_exception()

    try:
        forwarder.forward_messages()
    except MissingMeshHeader:
        pytest.fail("MissingMeshHeader was raised when it shouldn't have been")


def test_calls_logger_with_a_warning_when_message_is_missing_header():
    mock_mesh_inbox = MagicMock()
    mock_s3_uploader = MagicMock()
    mock_mesh_message = MagicMock()
    mock_mesh_message.id = "abc"

    mock_mesh_inbox.read_messages.return_value = iter([mock_mesh_message])
    forwarder = MeshToS3Forwarder(mock_mesh_inbox, mock_s3_uploader)
    mock_mesh_message.validate.side_effect = _a_missing_header_exception(
        header_name="fruit_header",
    )
    logger = logging.getLogger("s3mesh.forwarder")

    with mock.patch.object(logger, "warning") as mock_warn:
        forwarder.forward_messages()

    mock_warn.assert_called_with("Message abc: Missing MESH fruit_header header")


def test_continues_uploading_messages_when_one_of_them_has_missing_mesh_header():
    mock_mesh_inbox = MagicMock()
    mock_s3_uploader = MagicMock()
    successful_message_1 = MagicMock()
    successful_message_2 = MagicMock()
    unsuccessful_message = MagicMock()
    unsuccessful_message.validate.side_effect = _a_missing_header_exception()

    mock_mesh_inbox.read_messages.return_value = iter(
        [successful_message_1, unsuccessful_message, successful_message_2]
    )

    forwarder = MeshToS3Forwarder(mock_mesh_inbox, mock_s3_uploader)

    forwarder.forward_messages()

    mock_s3_uploader.upload.assert_has_calls(
        [
            call(successful_message_1),
            call(successful_message_2),
        ]
    )


def test_does_not_catch_generic_exception():
    mock_mesh_inbox = MagicMock()
    mock_s3_uploader = MagicMock()
    mock_mesh_message = MagicMock()
    mock_mesh_inbox.read_messages.return_value = iter([mock_mesh_message])
    forwarder = MeshToS3Forwarder(mock_mesh_inbox, mock_s3_uploader)
    mock_mesh_message.validate.side_effect = Exception

    with pytest.raises(Exception):
        forwarder.forward_messages()
