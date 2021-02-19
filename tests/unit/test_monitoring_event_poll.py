from mock import MagicMock

from s3mesh.monitoring.event.poll import POLL_INBOX_EVENT, PollInboxEvent


def test_finish_calls_log_event_with_event_name():
    mock_output = MagicMock()

    poll_inbox_event = PollInboxEvent(mock_output)
    poll_inbox_event.finish()

    mock_output.log_event.assert_called_with(POLL_INBOX_EVENT, {})


def test_record_message_batch_count():
    mock_output = MagicMock()

    poll_inbox_event = PollInboxEvent(mock_output)
    poll_inbox_event.record_message_batch_count(2)
    poll_inbox_event.finish()

    mock_output.log_event.assert_called_with(POLL_INBOX_EVENT, {"batchMessageCount": 2})
