from unittest.mock import MagicMock, call

import pytest

from s3mesh.forwarder import (
    FORWARD_MESSAGE_EVENT,
    INVALID_MESH_HEADER_ERROR,
    MESH_CLIENT_NETWORK_ERROR,
    MISSING_MESH_HEADER_ERROR,
    POLL_MESSAGE_EVENT,
    RetryableException,
)
from s3mesh.mesh import InvalidMeshHeader, MissingMeshHeader
from tests.builders.common import a_string
from tests.builders.forwarder import build_forwarder
from tests.builders.mesh import mesh_client_error, mock_mesh_message


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
    mock_message = mock_mesh_message()

    forwarder = build_forwarder(
        incoming_messages=[mock_message],
    )

    forwarder.forward_messages()

    mock_message.validate.assert_called_once()


def test_forwards_message():
    mock_message = mock_mesh_message()
    mock_uploader = MagicMock()
    probe = MagicMock()
    observation = MagicMock()
    probe.start_observation.return_value = observation

    forwarder = build_forwarder(
        incoming_messages=[mock_message], s3_uploader=mock_uploader, probe=probe
    )

    forwarder.forward_messages()

    mock_uploader.upload.assert_called_once_with(mock_message, observation)


def test_acknowledges_message():
    mock_message = mock_mesh_message()

    forwarder = build_forwarder(
        incoming_messages=[mock_message],
    )

    forwarder.forward_messages()

    mock_message.acknowledge.assert_called_once()


def test_forwards_multiple_messages():
    mock_message_one = mock_mesh_message()
    mock_message_two = mock_mesh_message()
    mock_uploader = MagicMock()
    probe = MagicMock()
    observation = MagicMock()
    probe.start_observation.return_value = observation

    forwarder = build_forwarder(
        incoming_messages=[mock_message_one, mock_message_two],
        s3_uploader=mock_uploader,
        probe=probe,
    )

    forwarder.forward_messages()

    mock_uploader.upload.assert_has_calls(
        [
            call(mock_message_one, observation),
            call(mock_message_two, observation),
        ]
    )

    assert mock_uploader.upload.call_count == 2


def test_acknowledges_multiple_message():

    mock_messages = [mock_mesh_message(), mock_mesh_message()]

    forwarder = build_forwarder(incoming_messages=mock_messages)

    forwarder.forward_messages()

    for mock_message in mock_messages:
        mock_message.acknowledge.assert_called_once()


def test_catches_invalid_header_error():
    forwarder = build_forwarder(
        incoming_messages=[mock_mesh_message(validation_error=_an_invalid_header_exception())]
    )

    try:
        forwarder.forward_messages()
    except InvalidMeshHeader:
        pytest.fail("InvalidMeshHeader was raised when it shouldn't have been")


def test_continues_uploading_messages_when_one_of_them_has_invalid_mesh_header():
    successful_message_1 = mock_mesh_message()
    successful_message_2 = mock_mesh_message()
    unsuccessful_message = mock_mesh_message(validation_error=_an_invalid_header_exception())
    mock_uploader = MagicMock()
    probe = MagicMock()
    observation = MagicMock()
    probe.start_observation.return_value = observation

    forwarder = build_forwarder(
        incoming_messages=[successful_message_1, unsuccessful_message, successful_message_2],
        s3_uploader=mock_uploader,
        probe=probe,
    )

    forwarder.forward_messages()

    mock_uploader.upload.assert_has_calls(
        [
            call(successful_message_1, observation),
            call(successful_message_2, observation),
        ]
    )


def test_catches_missing_header_error():
    forwarder = build_forwarder(
        incoming_messages=[mock_mesh_message(validation_error=_a_missing_header_exception())]
    )

    try:
        forwarder.forward_messages()
    except MissingMeshHeader:
        pytest.fail("MissingMeshHeader was raised when it shouldn't have been")


def test_continues_uploading_messages_when_one_of_them_has_missing_mesh_header():
    successful_message_1 = mock_mesh_message()
    successful_message_2 = mock_mesh_message()
    unsuccessful_message = mock_mesh_message(validation_error=_a_missing_header_exception())

    mock_uploader = MagicMock()
    probe = MagicMock()
    observation = MagicMock()
    probe.start_observation.return_value = observation

    forwarder = build_forwarder(
        incoming_messages=[successful_message_1, unsuccessful_message, successful_message_2],
        s3_uploader=mock_uploader,
        probe=probe,
    )

    forwarder.forward_messages()

    mock_uploader.upload.assert_has_calls(
        [
            call(successful_message_1, observation),
            call(successful_message_2, observation),
        ]
    )


def test_does_not_catch_generic_exception():
    forwarder = build_forwarder(incoming_messages=[mock_mesh_message(validation_error=Exception)])

    with pytest.raises(Exception):
        forwarder.forward_messages()


def test_records_message_progress():
    probe = MagicMock()
    poll_observation = MagicMock()
    forward_observation = MagicMock()
    probe.start_observation.side_effect = [poll_observation, forward_observation]

    forwarder = build_forwarder(
        incoming_messages=[
            mock_mesh_message(
                message_id="123", sender="mesh123", recipient="mesh456", file_name="a_file.dat"
            )
        ],
        probe=probe,
    )

    forwarder.forward_messages()

    probe.start_observation.assert_has_calls(
        [call(POLL_MESSAGE_EVENT), call(FORWARD_MESSAGE_EVENT)], any_order=False
    )
    poll_observation.assert_has_calls(
        [call.add_field("polledMessages", 1), call.finish()], any_order=False
    )
    forward_observation.assert_has_calls(
        [
            call.add_field("messageId", "123"),
            call.add_field("sender", "mesh123"),
            call.add_field("recipient", "mesh456"),
            call.add_field("fileName", "a_file.dat"),
            call.finish(),
        ],
        any_order=False,
    )


def test_records_error_when_message_is_missing_header():
    probe = MagicMock()
    observation = MagicMock()
    probe.start_observation.side_effect = [MagicMock(), observation]

    forwarder = build_forwarder(
        incoming_messages=[
            mock_mesh_message(
                message_id="abc",
                sender="mesh123",
                recipient="mesh456",
                file_name="a_file.dat",
                validation_error=_a_missing_header_exception(
                    header_name="fruit_header",
                ),
            )
        ],
        probe=probe,
    )

    forwarder.forward_messages()

    probe.start_observation.assert_called_with(FORWARD_MESSAGE_EVENT)
    observation.assert_has_calls(
        [
            call.add_field("messageId", "abc"),
            call.add_field("sender", "mesh123"),
            call.add_field("recipient", "mesh456"),
            call.add_field("fileName", "a_file.dat"),
            call.add_field("error", MISSING_MESH_HEADER_ERROR),
            call.add_field("missingHeaderName", "fruit_header"),
            call.finish(),
        ],
        any_order=False,
    )


def test_records_error_when_message_has_invalid_header():
    probe = MagicMock()
    observation = MagicMock()
    probe.start_observation.side_effect = [MagicMock(), observation]

    forwarder = build_forwarder(
        incoming_messages=[
            mock_mesh_message(
                message_id="abc",
                file_name="a_file.dat",
                sender="mesh123",
                recipient="mesh456",
                validation_error=_an_invalid_header_exception(
                    header_name="fruit_header",
                    header_value="banana",
                    expected_header_value="mango",
                ),
            )
        ],
        probe=probe,
    )

    forwarder.forward_messages()

    probe.start_observation.assert_called_with(FORWARD_MESSAGE_EVENT)
    observation.assert_has_calls(
        [
            call.add_field("messageId", "abc"),
            call.add_field("sender", "mesh123"),
            call.add_field("recipient", "mesh456"),
            call.add_field("fileName", "a_file.dat"),
            call.add_field("error", INVALID_MESH_HEADER_ERROR),
            call.add_field("expectedHeaderValue", "mango"),
            call.add_field("receivedHeaderValue", "banana"),
            call.finish(),
        ],
        any_order=False,
    )


def test_raises_retryable_exception_when_inbox_read_messages_raises_mesh_network_exception():
    forwarder = build_forwarder(read_error=mesh_client_error("Network error"))

    with pytest.raises(RetryableException) as e:
        forwarder.forward_messages()

    assert e.value.error_message == "Network error"


def test_raises_retryable_exception_when_mesh_message_ack_raises_mesh_network_exception():
    mock_message = mock_mesh_message(acknowledge_error=mesh_client_error("Network error"))
    forwarder = build_forwarder(incoming_messages=[mock_message])

    with pytest.raises(RetryableException) as e:
        forwarder.forward_messages()

    assert e.value.error_message == "Network error"


def test_records_error_when_mesh_message_ack_raises_mesh_network_exception():
    probe = MagicMock()
    observation = MagicMock()
    probe.start_observation.side_effect = [MagicMock(), observation]

    mock_message = mock_mesh_message(
        message_id="abc",
        file_name="a_file.dat",
        sender="mesh123",
        recipient="mesh456",
        acknowledge_error=mesh_client_error("Network error"),
    )

    forwarder = build_forwarder(incoming_messages=[mock_message], probe=probe)

    with pytest.raises(RetryableException):
        forwarder.forward_messages()

    probe.start_observation.assert_called_with(FORWARD_MESSAGE_EVENT)

    observation.assert_has_calls(
        [
            call.add_field("messageId", "abc"),
            call.add_field("sender", "mesh123"),
            call.add_field("recipient", "mesh456"),
            call.add_field("fileName", "a_file.dat"),
            call.add_field("error", MESH_CLIENT_NETWORK_ERROR),
            call.add_field(
                "errorMessage",
                "Network error",
            ),
            call.finish(),
        ],
        any_order=False,
    )


def test_records_mesh_error_when_polling_messages():
    probe = MagicMock()
    observation = MagicMock()
    probe.start_observation.return_value = observation

    forwarder = build_forwarder(probe=probe, read_error=mesh_client_error())
    with pytest.raises(RetryableException):
        forwarder.forward_messages()

    probe.start_observation.assert_called_once_with(POLL_MESSAGE_EVENT)
    observation.assert_has_calls(
        [
            call.add_field("error", MESH_CLIENT_NETWORK_ERROR),
            call.add_field(
                "errorMessage",
                "A message",
            ),
            call.finish(),
        ],
        any_order=False,
    )


def test_returns_false_if_mailbox_is_not_empty():
    mesh_inbox = MagicMock()
    mesh_inbox.count_messages.return_value = 1

    forwarder = build_forwarder(mesh_inbox=mesh_inbox)

    assert forwarder.is_mailbox_empty() is False


def test_returns_true_if_mailbox_is_empty():
    mesh_inbox = MagicMock()
    mesh_inbox.count_messages.return_value = 0

    forwarder = build_forwarder(mesh_inbox=mesh_inbox)

    assert forwarder.is_mailbox_empty() is True


def test_raises_retryable_exception_when_inbox_count_messages_raises_mesh_network_exception():
    forwarder = build_forwarder(count_error=mesh_client_error("Network error"))

    with pytest.raises(RetryableException) as e:
        forwarder.is_mailbox_empty()

    assert e.value.error_message == "Network error"
