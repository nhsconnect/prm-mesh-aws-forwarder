from s3mesh.mesh import MeshMessage
from s3mesh.monitoring.event.forward import ForwardMessageEvent


class SNSUploader:
    def __init__(self, sns_client, topic_arn: str):
        self._sns_client = sns_client
        self.topic_arn = topic_arn

    def upload(self, message: MeshMessage, forward_message_event: ForwardMessageEvent):
        message_content = message.read().decode("utf-8")
        response = self._sns_client.publish(TopicArn=self.topic_arn, Message=message_content)
        forward_message_event.record_sns_message_id(response["MessageId"])
