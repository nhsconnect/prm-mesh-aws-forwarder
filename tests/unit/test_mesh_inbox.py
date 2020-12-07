import logging
from unittest import mock
from unittest.mock import MagicMock

import pytest

from s3mesh.mesh import MeshInbox
from tests.builders.common import a_string
from tests.builders.mesh import build_mex_headers, mock_client_message


def test_returns_messages():
    mock_mesh_client = MagicMock()
    mocked_message_ids = [a_string(), a_string(), a_string()]
    client_messages = [mock_client_message(message_id=m_id) for m_id in mocked_message_ids]
    mock_mesh_client.iterate_all_messages.return_value = iter(client_messages)
    mesh_inbox = MeshInbox(mock_mesh_client)

    actual_messages_ids = [message.id for message in mesh_inbox.read_messages()]

    assert actual_messages_ids == mocked_message_ids


def test_catches_exception():
    mock_mesh_client = MagicMock()
    unsuccessful_message = mock_client_message(
        mex_headers=build_mex_headers(status_event="COLLECT")
    )
    client_messages = [unsuccessful_message]
    mock_mesh_client.iterate_all_messages.return_value = iter(client_messages)
    mesh_inbox = MeshInbox(mock_mesh_client)

    actual_messages = list(mesh_inbox.read_messages())
    expected_messages = []

    assert actual_messages == expected_messages


def test_continues_reading_messages_when_one_of_them_throws_exception():
    mock_mesh_client = MagicMock()
    successful_message_1 = mock_client_message(message_id=a_string())
    successful_message_2 = mock_client_message(message_id=a_string())
    unsuccessful_message = mock_client_message(
        message_id=a_string(), mex_headers=build_mex_headers(status_success="ERROR")
    )

    client_messages = [successful_message_1, unsuccessful_message, successful_message_2]
    mock_mesh_client.iterate_all_messages.return_value = iter(client_messages)
    mesh_inbox = MeshInbox(mock_mesh_client)

    actual_message_ids = [message.id for message in mesh_inbox.read_messages()]
    expected_message_ids = [successful_message_1.id(), successful_message_2.id()]

    assert actual_message_ids == expected_message_ids


def test_does_not_catch_generic_exception():
    mock_mesh_client = MagicMock()
    unsuccessful_message = mock_client_message()
    unsuccessful_message.id.side_effect = Exception()
    client_messages = [unsuccessful_message]
    mock_mesh_client.iterate_all_messages.return_value = iter(client_messages)
    mesh_inbox = MeshInbox(mock_mesh_client)

    with pytest.raises(Exception):
        list(mesh_inbox.read_messages())


def test_calls_logger_with_a_warning_when_header_statussuccess_is_not_success():
    logger = logging.getLogger("s3mesh.mesh")
    mock_mesh_client = MagicMock()
    message_id = a_string()
    error_status = "ERROR"
    unsuccessful_message = mock_client_message(
        message_id=message_id, mex_headers=build_mex_headers(status_success=error_status)
    )
    client_messages = [unsuccessful_message]
    mock_mesh_client.iterate_all_messages.return_value = iter(client_messages)
    mesh_inbox = MeshInbox(mock_mesh_client)

    with mock.patch.object(logger, "warning") as mock_warn:
        list(mesh_inbox.read_messages())

    mock_warn.assert_called_with(f"Message {message_id}: unexpected status header {error_status}")
