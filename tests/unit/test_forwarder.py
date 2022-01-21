from unittest import mock
from unittest.mock import MagicMock, call

import pytest

from awsmesh.forwarder import RetryableException
from awsmesh.mesh import InvalidMeshHeader, MissingMeshHeader
from awsmesh.uploader import UploaderError
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
    forward_message_event = MagicMock()
    probe.new_forward_message_event.return_value = forward_message_event

    forwarder = build_forwarder(
        incoming_messages=[mock_message], uploader=mock_uploader, probe=probe
    )

    forwarder.forward_messages()

    mock_uploader.upload.assert_called_once_with(mock_message, forward_message_event)


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
    forward_message_event = MagicMock()
    probe.new_forward_message_event.return_value = forward_message_event

    forwarder = build_forwarder(
        incoming_messages=[mock_message_one, mock_message_two],
        uploader=mock_uploader,
        probe=probe,
    )

    forwarder.forward_messages()

    mock_uploader.upload.assert_has_calls(
        [
            call(mock_message_one, forward_message_event),
            call(mock_message_two, forward_message_event),
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


def test_uploads_message_with_unexpected_mesh_header_if_validation_is_disabled():
    message_with_unexpected_header = mock_mesh_message(
        validation_error=_an_invalid_header_exception()
    )
    mock_uploader = MagicMock()

    forwarder = build_forwarder(
        incoming_messages=[message_with_unexpected_header],
        uploader=mock_uploader,
        disable_message_header_validation=True,
    )

    forwarder.forward_messages()

    mock_uploader.upload.assert_has_calls(
        [
            call(message_with_unexpected_header, mock.ANY),
        ]
    )


def test_continues_uploading_messages_when_one_of_them_has_invalid_mesh_header():
    successful_message_1 = mock_mesh_message()
    successful_message_2 = mock_mesh_message()
    unsuccessful_message = mock_mesh_message(validation_error=_an_invalid_header_exception())
    mock_uploader = MagicMock()
    probe = MagicMock()
    forward_message_event = MagicMock()
    probe.new_forward_message_event.return_value = forward_message_event

    forwarder = build_forwarder(
        incoming_messages=[successful_message_1, unsuccessful_message, successful_message_2],
        uploader=mock_uploader,
        probe=probe,
    )

    forwarder.forward_messages()

    mock_uploader.upload.assert_has_calls(
        [
            call(successful_message_1, forward_message_event),
            call(successful_message_2, forward_message_event),
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
    forward_message_event = MagicMock()
    probe.new_forward_message_event.return_value = forward_message_event

    forwarder = build_forwarder(
        incoming_messages=[successful_message_1, unsuccessful_message, successful_message_2],
        uploader=mock_uploader,
        probe=probe,
    )

    forwarder.forward_messages()

    mock_uploader.upload.assert_has_calls(
        [
            call(successful_message_1, forward_message_event),
            call(successful_message_2, forward_message_event),
        ]
    )


def test_does_not_catch_generic_exception():
    forwarder = build_forwarder(incoming_messages=[mock_mesh_message(validation_error=Exception)])

    with pytest.raises(Exception):
        forwarder.forward_messages()


def test_records_message_progress():
    probe = MagicMock()
    mesh_message = mock_mesh_message()
    forwarder = build_forwarder(
        incoming_messages=[mesh_message],
        probe=probe,
    )

    forwarder.forward_messages()

    probe.assert_has_calls(
        [
            call.new_poll_inbox_event(),
            call.new_poll_inbox_event().record_message_batch_count(1),
            call.new_poll_inbox_event().finish(),
            call.new_forward_message_event(),
            call.new_forward_message_event().record_message_metadata(mesh_message),
            call.new_forward_message_event().finish(),
        ]
    )


def test_records_error_when_message_is_missing_header():
    probe = MagicMock()
    forward_message_event = MagicMock()
    probe.new_forward_message_event.return_value = forward_message_event
    header_error = _a_missing_header_exception(
        header_name="fruit_header",
    )
    message = mock_mesh_message(
        validation_error=header_error,
    )

    forwarder = build_forwarder(
        incoming_messages=[message],
        probe=probe,
    )

    forwarder.forward_messages()

    forward_message_event.assert_has_calls(
        [
            call.record_message_metadata(message),
            call.record_missing_mesh_header(header_error),
            call.finish(),
        ],
        any_order=False,
    )


def test_records_error_when_message_has_invalid_header():
    probe = MagicMock()
    forward_message_event = MagicMock()
    probe.new_forward_message_event.return_value = forward_message_event
    header_error = _an_invalid_header_exception(
        header_name="fruit_header",
    )
    message = mock_mesh_message(
        validation_error=header_error,
    )

    forwarder = build_forwarder(
        incoming_messages=[message],
        probe=probe,
    )

    forwarder.forward_messages()

    forward_message_event.assert_has_calls(
        [
            call.record_message_metadata(message),
            call.record_invalid_mesh_header(header_error),
            call.finish(),
        ],
        any_order=False,
    )


def test_raises_retryable_exception_when_inbox_read_messages_raises_mesh_network_exception():
    forwarder = build_forwarder(read_error=mesh_client_error())

    with pytest.raises(RetryableException):
        forwarder.forward_messages()


def test_raises_retryable_exception_when_mesh_message_ack_raises_mesh_network_exception():
    mock_message = mock_mesh_message(acknowledge_error=mesh_client_error())
    forwarder = build_forwarder(incoming_messages=[mock_message])

    with pytest.raises(RetryableException):
        forwarder.forward_messages()


def test_records_error_when_mesh_message_ack_raises_mesh_network_exception():
    probe = MagicMock()
    forward_message_event = MagicMock()
    probe.new_forward_message_event.return_value = forward_message_event
    network_error = mesh_client_error("Network error")
    mock_message = mock_mesh_message(
        acknowledge_error=network_error,
    )

    forwarder = build_forwarder(incoming_messages=[mock_message], probe=probe)

    with pytest.raises(RetryableException):
        forwarder.forward_messages()

    forward_message_event.assert_has_calls(
        [
            call.record_message_metadata(mock_message),
            call.record_mesh_client_network_error(network_error),
            call.finish(),
        ],
        any_order=False,
    )


def test_records_mesh_error_when_polling_messages():
    probe = MagicMock()
    poll_inbox_event = MagicMock()
    probe.new_poll_inbox_event.return_value = poll_inbox_event

    client_error = mesh_client_error()
    forwarder = build_forwarder(probe=probe, read_error=client_error)
    with pytest.raises(RetryableException):
        forwarder.forward_messages()

    poll_inbox_event.assert_has_calls(
        [call.record_mesh_client_network_error(client_error), call.finish()],
        any_order=False,
    )


def test_returns_false_if_mailbox_is_not_empty():
    forwarder = build_forwarder(inbox_message_count=1)

    assert forwarder.is_mailbox_empty() is False


def test_returns_true_if_mailbox_is_empty():
    forwarder = build_forwarder(inbox_message_count=0)

    assert forwarder.is_mailbox_empty() is True


def test_returns_true_if_mailbox_count_is_less_than_zero():
    forwarder = build_forwarder(inbox_message_count=-1)

    assert forwarder.is_mailbox_empty() is True


def test_raises_retryable_exception_when_inbox_count_messages_raises_mesh_network_exception():
    forwarder = build_forwarder(count_error=mesh_client_error())

    with pytest.raises(RetryableException):
        forwarder.is_mailbox_empty()


def test_records_inbox_message_count():
    probe = MagicMock()

    forwarder = build_forwarder(inbox_message_count=3, probe=probe)

    forwarder.is_mailbox_empty()

    probe.assert_has_calls(
        [
            call.new_count_messages_event(),
            call.new_count_messages_event().record_message_count(3),
            call.new_count_messages_event().finish(),
        ]
    )


def test_records_mesh_error_when_counting_messages():
    probe = MagicMock()

    network_error = mesh_client_error("Network error")
    forwarder = build_forwarder(count_error=network_error, probe=probe)

    with pytest.raises(RetryableException):
        forwarder.is_mailbox_empty()

    probe.assert_has_calls(
        [
            call.new_count_messages_event(),
            call.new_count_messages_event().record_mesh_client_network_error(network_error),
            call.new_count_messages_event().finish(),
        ]
    )


def test_records_error_when_message_uploader_raises_uploader_error():
    probe = MagicMock()
    forward_message_event = MagicMock()
    probe.new_forward_message_event.return_value = forward_message_event
    message = mock_mesh_message()
    exception = UploaderError("error_message")

    forwarder = build_forwarder(
        uploader_error=exception,
        incoming_messages=[message],
        probe=probe,
    )

    forwarder.forward_messages()

    forward_message_event.assert_has_calls(
        [
            call.record_message_metadata(message),
            call.record_uploader_error(exception),
            call.finish(),
        ],
        any_order=False,
    )
