from unittest.mock import MagicMock

from s3mesh.mesh import MeshInbox
from tests.builders.common import a_string
from tests.builders.mesh import mock_client_message


def test_returns_messages():
    mock_mesh_client = MagicMock()
    mocked_message_ids = [a_string(), a_string(), a_string()]
    client_messages = [mock_client_message(message_id=m_id) for m_id in mocked_message_ids]
    mock_mesh_client.iterate_all_messages.return_value = iter(client_messages)
    mesh_inbox = MeshInbox(mock_mesh_client)

    actual_messages_ids = [message.id for message in mesh_inbox.read_messages()]

    assert actual_messages_ids == mocked_message_ids
