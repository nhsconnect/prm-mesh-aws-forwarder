import pytest
from requests import RequestException

from s3mesh.mesh import MeshClientNetworkError
from tests.builders.common import a_string
from tests.builders.mesh import mock_client_message, mock_mesh_inbox


def _mesh_client_network_error():
    return RequestException()


def test_returns_messages():
    message_ids = [a_string(), a_string(), a_string()]
    client_messages = [mock_client_message(message_id=m_id) for m_id in message_ids]
    mesh_inbox = mock_mesh_inbox(client_messages=client_messages)

    actual_messages_ids = [message.id for message in mesh_inbox.read_messages()]

    assert actual_messages_ids == message_ids


def test_raises_custom_exception_when_mesh_client_responds_with_an_error():
    mesh_inbox = mock_mesh_inbox(error=_mesh_client_network_error())

    with pytest.raises(MeshClientNetworkError):
        list(mesh_inbox.read_messages())
