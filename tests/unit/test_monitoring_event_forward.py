from mock import MagicMock

from s3mesh.forwarder import MISSING_MESH_HEADER_ERROR
from s3mesh.mesh import MissingMeshHeader
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
