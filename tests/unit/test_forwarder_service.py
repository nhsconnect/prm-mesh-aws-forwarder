from unittest.mock import MagicMock

from s3mesh.forwarder_service import MeshToS3ForwarderService


def test_calls_forward_messages_multiple_times_until_exit_event_is_set():
    forwarder = MagicMock()
    forwarder.is_mailbox_empty.return_value = True
    exit_event = MagicMock()
    exit_event.is_set.side_effect = [False, False, False, True]

    forwarder_service = MeshToS3ForwarderService(
        forwarder=forwarder, poll_frequency_sec=0, exit_event=exit_event
    )
    forwarder_service.start()

    assert forwarder.forward_messages.call_count == 3
