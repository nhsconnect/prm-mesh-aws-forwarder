from unittest.mock import MagicMock

from requests import ConnectionError, HTTPError, Request, Response

from s3mesh.mesh import (
    MESH_MESSAGE_TYPE_DATA,
    MESH_STATUS_EVENT_TRANSFER,
    MESH_STATUS_SUCCESS,
    MeshClientNetworkError,
    MeshInbox,
)
from tests.builders.common import a_datetime, a_string

TEST_INBOX_URL = "https://mesh.test.test.uk/messageexchange/test_inbox/inbox"


def an_epoch_timestamp():
    return a_datetime().timestamp()


def a_timestamp():
    return a_datetime().strftime("%Y%m%d%H%M%S")


def a_filename(timestamp):
    return f"{timestamp}_{a_string()}.dat"


def build_mex_headers(**kwargs):
    mocked_timestamp = a_timestamp()

    return {
        "statusevent": kwargs.get("status_event", MESH_STATUS_EVENT_TRANSFER),
        "addresstype": kwargs.get("address_type", "ALL"),
        "statustimestamp": kwargs.get("status_timestamp", mocked_timestamp),
        "fromsmtp": kwargs.get("from_smtp", a_string()),
        "content-compressed": kwargs.get("content_compressed", "N"),
        "tosmtp": kwargs.get("to_smtp", a_string()),
        "statusdescription": kwargs.get("status_description", "Transferred to recipient mailbox"),
        "version": kwargs.get("version", "1.0"),
        "statussuccess": kwargs.get("status_success", MESH_STATUS_SUCCESS),
        "statuscode": kwargs.get("status_code", "00"),
        "to": kwargs.get("to", a_string()),
        "messagetype": kwargs.get("message_type", MESH_MESSAGE_TYPE_DATA),
        "filename": kwargs.get("file_name", a_filename(mocked_timestamp)),
        "messageid": kwargs.get("message_id", a_string()),
        "from": kwargs.get("from", a_string()),
    }


def mock_client_message(**kwargs):
    mex_headers = kwargs.get("mex_headers", build_mex_headers())
    message = MagicMock()
    message.id.return_value = kwargs.get("message_id", a_string())
    message.mex_header = lambda key: mex_headers[key]
    return message


def mock_mesh_inbox(client_messages=None, iterate_messages_error=None, count_messages_error=None):
    client_messages = [] if client_messages is None else client_messages
    mock_mesh_client = MagicMock()
    mock_mesh_client.iterate_all_messages.return_value = iter(client_messages)
    mock_mesh_client.iterate_all_messages.side_effect = iterate_messages_error
    mock_mesh_client.count_messages.side_effect = count_messages_error
    return MeshInbox(mock_mesh_client)


def mesh_client_http_error():
    response = Response()
    response.status_code = 400
    response.reason = "Bad request for url"
    response.url = TEST_INBOX_URL
    return HTTPError(response=response)


def mesh_client_connection_error():
    request = Request()
    request.url = TEST_INBOX_URL
    return ConnectionError(request=request)


def mesh_client_error():
    return MeshClientNetworkError("A message")
