import logging

from botocore.exceptions import ClientError

from awsmesh.mesh import MeshMessage
from awsmesh.uploader import UploaderError, UploadEventMetadata

logger = logging.getLogger(__name__)

# flake8: noqa: C901
class SNSUploader:
    def __init__(self, sns_client, topic_arn: str):
        self._sns_client = sns_client
        self.topic_arn = topic_arn

    def upload(self, message: MeshMessage, upload_event_metadata: UploadEventMetadata):
        try:
            message_content = message.read().decode("utf-8")
            if message_content == "":
                upload_event_metadata.record_empty_message_error(message)
                return

            message_headers = message.headers
            message_id_key = "messageid"
            mesh_message_id_key = "meshMessageId"
            sns_attributes = {}

            if message_id_key in message_headers:
                # check that we can just use message.id
                message_id_from_headers = message_headers[message_id_key]
                logger.info(
                    "message id: from headers %s, from .id %s", message_id_from_headers, message.id
                )

                sns_attributes[mesh_message_id_key] = {
                    "DataType": "String",
                    "StringValue": message_id_from_headers,
                }

            response = self._sns_client.publish(
                TopicArn=self.topic_arn, Message=message_content, MessageAttributes=sns_attributes
            )
            upload_event_metadata.record_sns_message_id(response["MessageId"])
        except ClientError as error:
            if error.response["Error"]["Code"] == "InvalidParameter":
                upload_event_metadata.record_invalid_parameter_error(
                    error.response["Error"]["Message"]
                )
            raise UploaderError(str(error))
