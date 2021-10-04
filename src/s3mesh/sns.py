from botocore.exceptions import ClientError

from s3mesh.mesh import MeshMessage
from s3mesh.uploader import UploaderError, UploadEventMetadata


class SNSUploader:
    def __init__(self, sns_client, topic_arn: str):
        self._sns_client = sns_client
        self.topic_arn = topic_arn

    def upload(self, message: MeshMessage, upload_event_metadata: UploadEventMetadata):
        try:
            message_content = message.read().decode("utf-8")
            response = self._sns_client.publish(TopicArn=self.topic_arn, Message=message_content)
            upload_event_metadata.record_sns_message_id(response["MessageId"])
        except ClientError as e:
            raise UploaderError(str(e))
