from s3mesh.mesh import MeshClientNetworkError
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


def test_raises_network_error_when_iterating_all_messages_throws_an_http_error():
    mesh_inbox = mock_mesh_inbox(iterate_messages_error=mesh_client_http_error())

    try:
        mesh_inbox.read_messages()
    except MeshClientNetworkError as e:
        assert e.error_message == f"400 HTTP Error: Bad request for url: {TEST_INBOX_URL}"


def test_raises_network_error_when_iterating_all_messages_throws_a_connection_error():
    mesh_inbox = mock_mesh_inbox(iterate_messages_error=mesh_client_connection_error())

    try:
        mesh_inbox.read_messages()
    except MeshClientNetworkError as e:
        assert e.error_message == (
            f"ConnectionError received when attempting to connect to: {TEST_INBOX_URL}"
        )


def test_raises_network_error_when_counting_messages_throws_an_http_error():
    mesh_inbox = mock_mesh_inbox(count_messages_error=mesh_client_http_error())

    try:
        mesh_inbox.count_messages()
    except MeshClientNetworkError as e:
        assert e.error_message == f"400 HTTP Error: Bad request for url: {TEST_INBOX_URL}"


def test_raises_network_error_when_counting_messages_throws_a_connection_error():
    mesh_inbox = mock_mesh_inbox(count_messages_error=mesh_client_connection_error())

    try:
        mesh_inbox.count_messages()
    except MeshClientNetworkError as e:
        assert e.error_message == (
            f"ConnectionError received when attempting to connect to: {TEST_INBOX_URL}"
        )
