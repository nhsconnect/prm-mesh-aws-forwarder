from unittest.mock import MagicMock

import pytest

from s3mesh.forwarder_service import MessageDestinationConfig
from s3mesh.message_destination_resolver import UnknownMessageDestination, resolve_message_uploader
from s3mesh.s3 import S3Uploader
from s3mesh.sns import SNSUploader


def test_returns_s3_uploader_when_message_destination_is_s3():
    config = MessageDestinationConfig(
        message_destination="s3",
        s3_bucket_name="s3_bucket_name",
        s3_endpoint_url="s3_endpoint_url",
        sns_topic_arn=None,
    )
    aws = MagicMock()

    uploader = resolve_message_uploader(config, aws)

    aws.client.assert_called_once_with(service_name="s3", endpoint_url="s3_endpoint_url")
    assert isinstance(uploader, S3Uploader)


def test_returns_sns_uploader_when_message_destination_is_sns():
    config = MessageDestinationConfig(
        message_destination="sns",
        s3_bucket_name=None,
        s3_endpoint_url="endpoint_url",
        sns_topic_arn="some_arn",
    )
    aws = MagicMock()

    uploader = resolve_message_uploader(config, aws)

    aws.client.assert_called_once_with(service_name="sns", endpoint_url="endpoint_url")
    assert isinstance(uploader, SNSUploader)


def test_throws_exception_if_unknown_message_destination():
    config = MessageDestinationConfig(
        message_destination="unknown",
        s3_bucket_name=None,
        s3_endpoint_url=None,
        sns_topic_arn="some_arn",
    )
    with pytest.raises(UnknownMessageDestination):
        resolve_message_uploader(config)
