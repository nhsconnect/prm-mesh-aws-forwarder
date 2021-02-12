from unittest.mock import MagicMock

from s3mesh.monitoring.output import LoggingOutput


def test_log_event_calls_logger_info_with_event_name_and_fields():
    mock_logger = MagicMock()
    logging_output = LoggingOutput(mock_logger)
    event_name = "New Event"
    event_info = {"field": "field_value"}

    logging_output.log_event(event_name, fields=event_info)

    mock_logger.info.assert_called_with(f"Observed {event_name}", extra=event_info)
