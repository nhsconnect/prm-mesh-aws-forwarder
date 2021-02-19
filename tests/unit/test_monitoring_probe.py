import logging
from unittest.mock import MagicMock, patch

from s3mesh.monitoring.probe import LoggingProbe


def test_uses_default_logger():
    probe = LoggingProbe()
    logger = logging.getLogger("s3mesh.monitoring.probe")

    with patch.object(logger, "info") as mock_info:
        count_messages_event = probe.new_count_messages_event()
        count_messages_event.finish()

        mock_info.assert_called_once_with(
            "Observed COUNT_MESSAGES", extra={"event": "COUNT_MESSAGES"}
        )


def test_binds_count_messages_event_to_logger():
    mock_logger = MagicMock()

    probe = LoggingProbe(mock_logger)

    count_messages_event = probe.new_count_messages_event()

    count_messages_event.finish()

    mock_logger.info.assert_called_once_with(
        "Observed COUNT_MESSAGES", extra={"event": "COUNT_MESSAGES"}
    )


def test_observation_receives_name_from_probe():
    event_name = "an_event"
    probe = LoggingProbe()
    observation = probe.start_observation(event_name)

    logger = logging.getLogger("s3mesh.monitoring.probe")
    with patch.object(logger, "info") as mock_info:
        observation.finish()

    mock_info.assert_called_once_with(f"Observed {event_name}", extra={"event": event_name})
