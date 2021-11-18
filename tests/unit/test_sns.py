from unittest.mock import ANY, MagicMock

import pytest

from awsmesh.sns import SNSUploader
from awsmesh.uploader import UploaderError
from tests.builders.aws import build_client_error
from tests.builders.common import a_string


def test_upload_publishes_to_sns():
    mock_sns_client = MagicMock()
    topic_arn = "test_topic"
    mesh_message = MagicMock()
    mesh_message_value = "some_string"
    mesh_message.read.return_value = mesh_message_value.encode("utf-8")

    uploader = SNSUploader(mock_sns_client, topic_arn)
    uploader.upload(mesh_message, MagicMock())

    mock_sns_client.publish.assert_called_once_with(
        TopicArn=topic_arn, Message=mesh_message_value, MessageAttributes={}
    )


def test_upload_records_message_id():
    mock_sns_client = MagicMock()
    topic_arn = "test_topic"
    mesh_message = MagicMock()
    forward_message_event = MagicMock()
    message_id = a_string()
    mock_sns_client.publish.return_value = {"MessageId": message_id}

    uploader = SNSUploader(mock_sns_client, topic_arn)
    uploader.upload(mesh_message, forward_message_event)

    forward_message_event.record_sns_message_id.assert_called_once_with(message_id)


def test_upload_records_error_when_invalid_parameter_exception_raised():
    mock_sns_client = MagicMock()
    forward_message_event = MagicMock()
    mesh_message = MagicMock()

    mock_sns_client.publish.side_effect = build_client_error(
        code="InvalidParameter", message="boom"
    )

    uploader = SNSUploader(mock_sns_client, "some_topic_arn")
    uploader.upload(mesh_message, forward_message_event)

    forward_message_event.record_invalid_parameter_error.assert_called_once_with("boom")


def test_upload_error_raised_when_upload_raises_exception():
    mock_sns_client = MagicMock()
    topic_arn = "test_topic"
    mesh_message = MagicMock()
    uploader = SNSUploader(mock_sns_client, topic_arn)
    error_message = "test_error"
    mock_sns_client.publish.side_effect = build_client_error(message=error_message)

    with pytest.raises(UploaderError) as e:
        uploader.upload(mesh_message, MagicMock())

    assert error_message in str(e.value)


def test_upload_forwards_all_mesh_message_headers_as_sns_message_attributes():
    mock_sns_client = MagicMock()
    mesh_message = MagicMock()
    headers = {"bob": "foo", "sue": "too"}
    mesh_message.headers = headers

    expected_sns_message_attributes = {
        "bob": {"DataType": "String", "StringValue": "foo"},
        "sue": {"DataType": "String", "StringValue": "too"},
    }

    uploader = SNSUploader(mock_sns_client, "test_topic")
    uploader.upload(mesh_message, MagicMock())

    mock_sns_client.publish.assert_called_once_with(
        TopicArn=ANY, Message=ANY, MessageAttributes=expected_sns_message_attributes
    )
