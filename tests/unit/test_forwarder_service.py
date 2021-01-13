import logging
from unittest.mock import MagicMock, call, patch

from s3mesh.forwarder_service import MeshToS3ForwarderService


def test_calls_forward_messages_multiple_times_until_exit_event_is_set():
    forwarder = MagicMock()
    forwarder.is_mailbox_empty.return_value = False
    exit_event = MagicMock()
    exit_event.is_set.side_effect = [False, False, False, True]

    forwarder_service = MeshToS3ForwarderService(
        forwarder=forwarder, poll_frequency_sec=0, exit_event=exit_event
    )
    forwarder_service.start()

    assert forwarder.forward_messages.call_count == 3


def test_logs_start_and_exit_of_the_service():
    forwarder = MagicMock()
    forwarder.is_mailbox_empty.return_value = False
    exit_event = MagicMock()
    exit_event.is_set.return_value = True

    forwarder_service = MeshToS3ForwarderService(
        forwarder=forwarder, poll_frequency_sec=0, exit_event=exit_event
    )

    logger = logging.getLogger("s3mesh.forwarder_service")
    with patch.object(logger, "info") as mock_info:
        forwarder_service.start()

    mock_info.assert_has_calls(
        [call.info("Started forwarder service"), call.info("Exiting forwarder service")]
    )


def test_sets_exit_event_and_logs_request_to_stop_when_calling_stop():
    forwarder = MagicMock()
    exit_event = MagicMock()

    forwarder_service = MeshToS3ForwarderService(
        forwarder=forwarder, poll_frequency_sec=0, exit_event=exit_event
    )

    logger = logging.getLogger("s3mesh.forwarder_service")
    with patch.object(logger, "info") as mock_info:
        forwarder_service.stop()

    mock_info.assert_called_once_with("Received request to stop")
    exit_event.set.assert_called_once()


def test_waits_when_mailbox_is_empty():
    forwarder = MagicMock()
    forwarder.is_mailbox_empty.return_value = True
    exit_event = MagicMock()
    exit_event.is_set.side_effect = [False, True]

    forwarder_service = MeshToS3ForwarderService(
        forwarder=forwarder, poll_frequency_sec=60, exit_event=exit_event
    )
    forwarder_service.start()

    exit_event.wait.assert_called_once_with(60)


def test_does_not_wait_when_mailbox_is_not_empty():
    forwarder = MagicMock()
    forwarder.is_mailbox_empty.return_value = False
    exit_event = MagicMock()
    exit_event.is_set.side_effect = [False, True]

    forwarder_service = MeshToS3ForwarderService(
        forwarder=forwarder, poll_frequency_sec=60, exit_event=exit_event
    )
    forwarder_service.start()

    assert not exit_event.wait.called
