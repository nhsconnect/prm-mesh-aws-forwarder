import logging
from unittest.mock import MagicMock, call, patch

from s3mesh.probe import LoggingObservation, LoggingProbe


def test_observation_receives_name_from_probe():
    probe = LoggingProbe()
    observation = probe.start_observation("an_event")

    logger = logging.getLogger("s3mesh.probe")
    with patch.object(logger, "info") as mock_info:
        observation.finish()

    mock_info.assert_called_once_with("an_event", extra={})


def test_logs_single_observation():
    logger = MagicMock()
    observation = LoggingObservation("an_event", logger)

    observation.add_field("vegetable", "turnip")

    observation.finish()

    logger.info.assert_has_calls(
        [call.info("an_event", extra={"vegetable": "turnip"})], any_order=False
    )


def test_logs_multiple_observations():
    logger = MagicMock()
    observation = LoggingObservation("an_event", logger)

    observation.add_field("vegetable", "turnip")
    observation.add_field("fruit", "mango")

    observation.finish()

    logger.info.assert_has_calls(
        [call.info("an_event", extra={"vegetable": "turnip", "fruit": "mango"})], any_order=False
    )
