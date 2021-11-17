from botocore.exceptions import ClientError

from awsmesh.mesh import MeshMessage
from awsmesh.uploader import UploaderError, UploadEventMetadata


class SNSUploader:
    def __init__(self, sns_client, topic_arn: str):
        self._sns_client = sns_client
        self.topic_arn = topic_arn

    def upload(self, message: MeshMessage, upload_event_metadata: UploadEventMetadata):
        try:
            message_content = message.read().decode("utf-8")
            response = self._sns_client.publish(TopicArn=self.topic_arn, Message=message_content)
            upload_event_metadata.record_sns_message_id(response["MessageId"])
        except ClientError as error:
            if error.response["Error"]["Code"] == "InvalidParameter":
                upload_event_metadata.record_invalid_parameter_error(
                    error.response["Error"]["Message"]
                )
            else:
                raise UploaderError(str(error))
