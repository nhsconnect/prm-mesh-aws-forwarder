from unittest.mock import MagicMock

import pytest

from awsmesh.mesh import MeshClientNetworkError, MeshInbox
from tests.builders.common import a_string
from tests.builders.mesh import (
    TEST_INBOX_URL,
    mesh_client_connection_error,
    mesh_client_http_error,
    mock_client_message,
    mock_mesh_inbox,
)


def test_returns_messages():
    message_ids = [a_string(), a_string(), a_string()]
    client_messages = [mock_client_message(message_id=m_id) for m_id in message_ids]
    mesh_inbox = mock_mesh_inbox(client_messages=client_messages)

    actual_messages_ids = [message.id for message in mesh_inbox.read_messages()]

    assert actual_messages_ids == message_ids


def test_raises_network_error_when_iterating_all_messages_raises_an_http_error():
    def mock_iterate_all_messages():
        raise mesh_client_http_error()
        yield mock_client_message()

    client_inbox = MagicMock()
    client_inbox.iterate_all_messages = mock_iterate_all_messages

    mesh_inbox = MeshInbox(client_inbox)

    with pytest.raises(MeshClientNetworkError) as e:
        mesh_inbox.read_messages()

    assert e.value.error_message == f"400 HTTP Error: Bad request for url: {TEST_INBOX_URL}"


def test_raises_network_error_when_iterating_all_messages_raises_a_connection_error():
    def mock_iterate_all_messages():
        raise mesh_client_connection_error("an error")
        yield mock_client_message()

    client_inbox = MagicMock()
    client_inbox.iterate_all_messages = mock_iterate_all_messages

    mesh_inbox = MeshInbox(client_inbox)

    with pytest.raises(MeshClientNetworkError) as e:
        mesh_inbox.read_messages()

    assert e.value.error_message == (
        f"ConnectionError received when attempting to connect to: {TEST_INBOX_URL}"
        " caused by: an error"
    )


def test_raises_network_error_when_counting_messages_raises_an_http_error():
    mesh_inbox = mock_mesh_inbox(count_messages_error=mesh_client_http_error())

    with pytest.raises(MeshClientNetworkError) as e:
        mesh_inbox.count_messages()

    assert e.value.error_message == f"400 HTTP Error: Bad request for url: {TEST_INBOX_URL}"


def test_raises_network_error_when_counting_messages_raises_a_connection_error():
    mesh_inbox = mock_mesh_inbox(count_messages_error=mesh_client_connection_error("an error"))

    with pytest.raises(MeshClientNetworkError) as e:
        mesh_inbox.count_messages()

    assert e.value.error_message == (
        f"ConnectionError received when attempting to connect to: {TEST_INBOX_URL}"
        " caused by: an error"
    )
