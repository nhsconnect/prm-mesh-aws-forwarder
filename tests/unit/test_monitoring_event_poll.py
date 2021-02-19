from mock import MagicMock

from s3mesh.monitoring.event.poll import POLL_INBOX_EVENT, PollInboxEvent


def test_finish_calls_log_event_with_event_name():
    mock_output = MagicMock()

    forward_message_event = PollInboxEvent(mock_output)
    forward_message_event.finish()

    mock_output.log_event.assert_called_with(POLL_INBOX_EVENT, {})
