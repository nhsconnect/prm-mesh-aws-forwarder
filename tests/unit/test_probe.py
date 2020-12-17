import logging
from unittest.mock import MagicMock, call, patch

from s3mesh.probe import LoggingObservation, LoggingProbe


def test_calls_logger():
    probe = LoggingProbe()
    observation = probe.start_observation()

    logger = logging.getLogger("s3mesh.probe")
    with patch.object(logger, "info") as mock_info:
        observation.finish()

    mock_info.assert_called_once()


def test_logs_single_observation():
    logger = MagicMock()
    observation = LoggingObservation(logger)

    observation.add_field("vegetable", "turnip")

    observation.finish()

    logger.info.assert_has_calls(
        [call.info("Message", extra={"vegetable": "turnip"})], any_order=False
    )


def test_logs_multiple_observations():
    logger = MagicMock()
    observation = LoggingObservation(logger)

    observation.add_field("vegetable", "turnip")
    observation.add_field("fruit", "mango")

    observation.finish()

    logger.info.assert_has_calls(
        [call.info("Message", extra={"vegetable": "turnip", "fruit": "mango"})], any_order=False
    )
