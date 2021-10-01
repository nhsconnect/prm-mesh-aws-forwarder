import json
from threading import Thread

from s3mesh.entrypoint import build_forwarder_from_environment_variables
from tests.builders.common import a_string

SENDING_MESH_MAILBOX = "e2e-sns-test-mailbox-sender"
RECEIVING_MESH_MAILBOX = "e2e-sns-test-mailbox-receiver"

AWS_REGION = "us-west-1"

WAIT_60_SEC = {"Delay": 5, "MaxAttempts": 12}


class ThreadedForwarder:
    def __init__(self, forwarder):
        self._forwarder = forwarder
        self._thread = Thread(target=forwarder.start)

    def start(self):
        self._thread.start()

    def stop(self):
        self._forwarder.stop()
        self._thread.join()


def _build_sns_forwarder(config, sns_topic_arn):
    env_config = {
        **config,
        "MESSAGE_DESTINATION": "sns",
        "SNS_TOPIC_ARN": sns_topic_arn,
    }

    forwarder = build_forwarder_from_environment_variables(env_config)
    return ThreadedForwarder(forwarder)


def test_mesh_inbox_sns_forwarder(e2e_test_context):
    mesh = e2e_test_context.build_mesh_client(SENDING_MESH_MAILBOX)

    e2e_test_context.set_fake_aws_environment_vars()
    e2e_test_context.populate_ssm_parameters(
        test_name="test-sns", receiving_mailbox_name=RECEIVING_MESH_MAILBOX
    )
    sns = e2e_test_context.build_aws_client("sns")
    sqs = e2e_test_context.build_aws_client("sqs")

    sns.create_topic(Name="test-topic")
    queue_name = "test-queue"
    queue_url = sqs.create_queue(QueueName=queue_name)["QueueUrl"]
    topic_list_response = sns.list_topics()
    topic_arn = topic_list_response["Topics"][0]["TopicArn"]
    sqs_arn = e2e_test_context.get_service_arn("sqs")
    sns.subscribe(
        TopicArn=topic_arn,
        Protocol="sqs",
        Endpoint=f"{sqs_arn}:{queue_name}",
    )

    file_contents = a_string()

    forwarder = _build_sns_forwarder(
        sns_topic_arn=topic_arn,
        config=e2e_test_context.build_forwarder_config(test_name="test-sns"),
    )
    try:
        forwarder.start()
        mesh.send_message(RECEIVING_MESH_MAILBOX, file_contents.encode("utf-8"))
        messages = sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=5)["Messages"]
        message_body = json.loads(messages[0]["Body"])["Message"]

        assert message_body == file_contents
    finally:
        forwarder.stop()
        e2e_test_context.unset_fake_aws_environment_vars()
