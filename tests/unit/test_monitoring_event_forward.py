from unittest.mock import MagicMock

from s3mesh.mesh import InvalidMeshHeader, MissingMeshHeader
from s3mesh.monitoring.error import (
    INVALID_MESH_HEADER_ERROR,
    MESH_CLIENT_NETWORK_ERROR,
    MISSING_MESH_HEADER_ERROR,
)
from s3mesh.monitoring.event.forward import FORWARD_MESSAGE_EVENT, ForwardMessageEvent
from tests.builders.common import a_string
from tests.builders.mesh import mock_mesh_message


def test_finish_calls_log_event_with_event_name():
    mock_output = MagicMock()

    forward_message_event = ForwardMessageEvent(mock_output)
    forward_message_event.finish()

    mock_output.log_event.assert_called_with(FORWARD_MESSAGE_EVENT, {})


def test_record_message_metadata():
    mock_output = MagicMock()
    message = mock_mesh_message()

    forward_message_event = ForwardMessageEvent(mock_output)
    forward_message_event.record_message_metadata(message)
    forward_message_event.finish()

    mock_output.log_event.assert_called_with(
        FORWARD_MESSAGE_EVENT,
        {
            "messageId": message.id,
            "sender": message.sender,
            "recipient": message.recipient,
            "fileName": message.file_name,
        },
    )


def test_record_s3_key():
    mock_output = MagicMock()
    key = "/a/key"

    forward_message_event = ForwardMessageEvent(mock_output)
    forward_message_event.record_s3_key(key)
    forward_message_event.finish()

    mock_output.log_event.assert_called_with(FORWARD_MESSAGE_EVENT, {"s3Key": key})


def test_record_sns_message_id():
    mock_output = MagicMock()
    message_id = a_string()

    forward_message_event = ForwardMessageEvent(mock_output)
    forward_message_event.record_sns_message_id(message_id)
    forward_message_event.finish()

    mock_output.log_event.assert_called_with(FORWARD_MESSAGE_EVENT, {"snsMessageId": message_id})


def test_record_missing_mesh_header():
    mock_output = MagicMock()
    missing_header_exception = MissingMeshHeader(header_name=a_string())

    forward_message_event = ForwardMessageEvent(mock_output)
    forward_message_event.record_missing_mesh_header(missing_header_exception)
    forward_message_event.finish()

    mock_output.log_event.assert_called_with(
        FORWARD_MESSAGE_EVENT,
        {
            "error": MISSING_MESH_HEADER_ERROR,
            "missingHeaderName": missing_header_exception.header_name,
        },
    )


def test_record_invalid_mesh_header():
    mock_output = MagicMock()
    invalid_header_exception = InvalidMeshHeader(
        header_name=a_string(), header_value=a_string(), expected_header_value=a_string()
    )

    forward_message_event = ForwardMessageEvent(mock_output)
    forward_message_event.record_invalid_mesh_header(invalid_header_exception)
    forward_message_event.finish()

    mock_output.log_event.assert_called_with(
        FORWARD_MESSAGE_EVENT,
        {
            "error": INVALID_MESH_HEADER_ERROR,
            "headerName": invalid_header_exception.header_name,
            "expectedHeaderValue": invalid_header_exception.expected_header_value,
            "receivedHeaderValue": invalid_header_exception.header_value,
        },
    )


def test_record_mesh_client_network_error():
    mock_output = MagicMock()
    error_message = "Oh no!"
    mock_exception = MagicMock()
    mock_exception.error_message = error_message

    forward_message_event = ForwardMessageEvent(mock_output)
    forward_message_event.record_mesh_client_network_error(mock_exception)
    forward_message_event.finish()

    mock_output.log_event.assert_called_with(
        FORWARD_MESSAGE_EVENT, {"error": MESH_CLIENT_NETWORK_ERROR, "errorMessage": error_message}
    )
