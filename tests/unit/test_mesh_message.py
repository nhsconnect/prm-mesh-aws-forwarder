import pytest

from s3mesh.mesh import (
    MESH_MESSAGE_TYPE_DATA,
    MESH_STATUS_EVENT_TRANSFER,
    MESH_STATUS_SUCCESS,
    MeshMessage,
    UnexpectedMessageType,
    UnexpectedStatusEvent,
    UnsuccessfulStatus,
)
from tests.builders.common import a_datetime, a_string
from tests.builders.mesh import a_filename, a_timestamp, build_mex_headers, mock_client_message


def test_calls_acknowledge_on_underlying_client_message():
    client_message = mock_client_message()
    message = MeshMessage(client_message)

    message.acknowledge()

    client_message.acknowledge.assert_called_once()


def test_exposes_message_id():
    mocked_id = a_string()
    client_message = mock_client_message(message_id=mocked_id)
    message = MeshMessage(client_message)

    assert message.id == mocked_id


def test_calls_read_on_underlying_client_message():
    expected_value = "data"

    client_message = mock_client_message()
    client_message.read.return_value = expected_value
    message = MeshMessage(client_message)

    actual_value = message.read(n=43)

    client_message.read.assert_called_once_with(43)
    assert actual_value == expected_value


def test_exposes_filename():
    mocked_timestamp = a_timestamp()
    mocked_filename = a_filename(mocked_timestamp)
    client_message = mock_client_message(mex_headers=build_mex_headers(file_name=mocked_filename))
    message = MeshMessage(client_message)

    assert message.file_name == mocked_filename


def test_exposes_date_delivered():
    date_delivered = a_datetime()
    status_timestamp_header = date_delivered.strftime("%Y%m%d%H%M%S")
    client_message = mock_client_message(
        mex_headers=build_mex_headers(status_timestamp=status_timestamp_header)
    )
    message = MeshMessage(client_message)

    assert message.date_delivered == date_delivered


def test_throws_exception_when_status_event_header_is_not_transfer():
    client_message = mock_client_message(mex_headers=build_mex_headers(status_event="COLLECT"))

    with pytest.raises(UnexpectedStatusEvent):
        MeshMessage(client_message)


def test_exception_records_header_when_status_event_header_is_not_transfer():
    message_id = a_string()
    status_event_header_value = "COLLECT"
    client_message = mock_client_message(
        message_id=message_id, mex_headers=build_mex_headers(status_event=status_event_header_value)
    )

    with pytest.raises(UnexpectedStatusEvent) as exception_info:
        MeshMessage(client_message)

    exception = exception_info.value
    assert exception.message_id == message_id
    assert exception.header_value == status_event_header_value
    assert exception.header_name == "statusevent"
    assert exception.expected_header_value == MESH_STATUS_EVENT_TRANSFER


def test_throws_exception_when_status_success_header_is_not_success():
    client_message = mock_client_message(mex_headers=build_mex_headers(status_success="ERROR"))

    with pytest.raises(UnsuccessfulStatus):
        MeshMessage(client_message)


def test_exception_records_header_when_status_success_header_is_not_success():
    message_id = a_string()
    status_success_header_value = "ERROR"
    client_message = mock_client_message(
        message_id=message_id,
        mex_headers=build_mex_headers(status_success=status_success_header_value),
    )

    with pytest.raises(UnsuccessfulStatus) as exception_info:
        MeshMessage(client_message)

    exception = exception_info.value
    assert exception.message_id == message_id
    assert exception.header_value == status_success_header_value
    assert exception.header_name == "statussuccess"
    assert exception.expected_header_value == MESH_STATUS_SUCCESS


def test_throws_exception_when_message_type_header_is_not_data():
    client_message = mock_client_message(mex_headers=build_mex_headers(message_type="REPORT"))

    with pytest.raises(UnexpectedMessageType):
        MeshMessage(client_message)


def test_exception_records_header_when_message_type_header_is_not_data():
    message_id = a_string()
    message_type_header_value = "REPORT"
    client_message = mock_client_message(
        message_id=message_id, mex_headers=build_mex_headers(message_type=message_type_header_value)
    )

    with pytest.raises(UnexpectedMessageType) as exception_info:
        MeshMessage(client_message)

    exception = exception_info.value
    assert exception.message_id == message_id
    assert exception.header_value == message_type_header_value
    assert exception.header_name == "messagetype"
    assert exception.expected_header_value == MESH_MESSAGE_TYPE_DATA
