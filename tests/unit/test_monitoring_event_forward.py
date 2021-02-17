from mock import MagicMock

from s3mesh.monitoring.event.forward import FORWARD_MESSAGE_EVENT, ForwardMessageEvent


def test_finish_calls_log_count_message_event():
    mock_output = MagicMock()
    count_messages_event = ForwardMessageEvent(mock_output)
    count_messages_event.finish()

    mock_output.log_event.assert_called_with(FORWARD_MESSAGE_EVENT, {})
