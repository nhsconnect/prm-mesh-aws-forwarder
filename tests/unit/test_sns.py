from unittest.mock import MagicMock

from s3mesh.sns import SNSUploader
from tests.builders.common import a_string


def test_upload():
    mock_sns_client = MagicMock()
    topic_arn = "test_topic"
    mesh_message = MagicMock()
    mesh_message_value = "some_string"
    mesh_message.read.return_value = mesh_message_value.encode("utf-8")

    uploader = SNSUploader(mock_sns_client, topic_arn)
    uploader.upload(mesh_message, MagicMock())

    mock_sns_client.publish.assert_called_once_with(TopicArn=topic_arn, Message=mesh_message_value)


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
