from dataclasses import dataclass
from typing import Optional, Protocol

import boto3

from s3mesh.mesh import MeshMessage
from s3mesh.monitoring.event.forward import ForwardMessageEvent
from s3mesh.s3 import S3Uploader
from s3mesh.sns import SNSUploader


@dataclass
class MessageDestinationConfig:
    message_destination: str
    s3_bucket_name: Optional[str]
    s3_endpoint_url: Optional[str]
    sns_topic_arn: Optional[str]


class MessageUploader(Protocol):
    def upload(self, message: MeshMessage, forward_message_event: ForwardMessageEvent):
        ...


class UnknownMessageDestination(Exception):
    pass


def resolve_message_uploader(config: MessageDestinationConfig, aws=boto3) -> MessageUploader:
    if config.message_destination == "s3":
        s3 = aws.client(
            service_name=config.message_destination, endpoint_url=config.s3_endpoint_url
        )
        return S3Uploader(s3, config.s3_bucket_name)
    elif config.message_destination == "sns":
        sns = aws.client(
            service_name=config.message_destination, endpoint_url=config.s3_endpoint_url
        )
        return SNSUploader(sns, config.sns_topic_arn)
    else:
        raise UnknownMessageDestination
