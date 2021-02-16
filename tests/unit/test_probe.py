from unittest.mock import MagicMock, call

from s3mesh.probe import LoggingObservation


def test_logs_single_observation():
    event_name = "an_event"
    logger = MagicMock()
    observation = LoggingObservation(event_name, logger)

    observation.add_field("vegetable", "turnip")

    observation.finish()

    logger.info.assert_has_calls(
        [call.info(f"Observed {event_name}", extra={"vegetable": "turnip", "event": event_name})],
        any_order=False,
    )


def test_logs_multiple_observations():
    event_name = "an_event"
    logger = MagicMock()
    observation = LoggingObservation(event_name, logger)

    observation.add_field("vegetable", "turnip")
    observation.add_field("fruit", "mango")

    observation.finish()

    logger.info.assert_has_calls(
        [
            call.info(
                f"Observed {event_name}",
                extra={"vegetable": "turnip", "fruit": "mango", "event": event_name},
            )
        ],
        any_order=False,
    )
