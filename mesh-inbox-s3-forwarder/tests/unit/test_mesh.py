from unittest.mock import MagicMock

from tests.builders.common import a_string, a_datetime
from s3mesh.mesh import MeshInbox, MeshMessage


def _a_timestamp():
    return a_datetime().strftime("%Y%m%d%H%M%S")


def _a_filename(timestamp):
    return f"{timestamp}_{a_string()}.dat"


def _build_mex_headers(**kwargs):
    mocked_timestamp = _a_timestamp()

    return {
        "statusevent": kwargs.get("status_event", "TRANSFER"),
        "addresstype": kwargs.get("address_type", "ALL"),
        "statustimestamp": kwargs.get("status_timestamp", mocked_timestamp),
        "fromsmtp": kwargs.get("from_smtp", a_string()),
        "content-compressed": kwargs.get("content_compressed", "N"),
        "tosmtp": kwargs.get("to_smtp", a_string()),
        "statusdescription": kwargs.get("status_description", "Transferred to recipient mailbox"),
        "version": kwargs.get("version", "1.0"),
        "statussuccess": kwargs.get("status_success", "SUCCESS"),
        "statuscode": kwargs.get("status_code", "00"),
        "to": kwargs.get("to", a_string()),
        "messagetype": kwargs.get("message_type", "DATA"),
        "filename": kwargs.get("file_name", _a_filename(mocked_timestamp)),
        "messageid": kwargs.get("message_id", a_string()),
        "from": kwargs.get("from", a_string()),
    }


def _mock_client_message(**kwargs):
    mex_headers = kwargs.get("mex_headers", _build_mex_headers())
    message = MagicMock()
    message.id.return_value = kwargs.get("message_id", a_string())
    message.mex_header = lambda key: mex_headers[key]
    return message


def test_mesh_inbox_returns_messages():
    mock_mesh_client = MagicMock()
    mocked_message_ids = [a_string(), a_string(), a_string()]
    client_messages = [_mock_client_message(message_id=m_id) for m_id in mocked_message_ids]
    mock_mesh_client.iterate_all_messages.return_value = iter(client_messages)
    mesh_inbox = MeshInbox(mock_mesh_client)

    actual_messages_ids = [message.id for message in mesh_inbox.read_messages()]

    assert actual_messages_ids == mocked_message_ids


def test_mesh_message_calls_acknowledge_on_underlying_client_message():
    client_message = MagicMock()
    message = MeshMessage(client_message)

    message.acknowledge()

    client_message.acknowledge.assert_called_once()


def test_mesh_message_exposes_message_id():
    mocked_id = a_string()
    client_message = _mock_client_message(message_id=mocked_id)
    message = MeshMessage(client_message)

    assert message.id == mocked_id


def test_mesh_message_calls_read_on_underlying_client_message():
    client_message = _mock_client_message()
    message = MeshMessage(client_message)

    message.read()

    client_message.read.assert_called_once()


def test_mesh_message_exposes_filename():
    mocked_timestamp = _a_timestamp()
    mocked_filename = _a_filename(mocked_timestamp)
    client_message = _mock_client_message(mex_headers=_build_mex_headers(file_name=mocked_filename))
    message = MeshMessage(client_message)

    assert message.filename == mocked_filename


def test_mesh_message_exposes_date_delivered():
    mocked_date_delivered = a_datetime().strftime("%Y%m%d%H%M%S")
    client_message = _mock_client_message(
        mex_headers=_build_mex_headers(status_timestamp=mocked_date_delivered)
    )
    message = MeshMessage(client_message)

    assert message.date_delivered == mocked_date_delivered
