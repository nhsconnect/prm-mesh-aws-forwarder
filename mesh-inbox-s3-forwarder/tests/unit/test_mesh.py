from unittest.mock import MagicMock

from s3mesh.mesh import MeshInbox, MeshMessage


def _mock_client_message(message_id):
    message = MagicMock()
    message.id.return_value = message_id
    return message


def test_mesh_inbox_returns_messages():
    mock_mesh_client = MagicMock()
    mocked_message_ids = ["a", "b", "c"]
    client_messages = [_mock_client_message(m_id) for m_id in mocked_message_ids]
    mock_mesh_client.iterate_all_messages.return_value = iter(client_messages)
    mesh_inbox = MeshInbox(mock_mesh_client)

    actual_messages_ids = [message.id for message in mesh_inbox.read_messages()]

    assert actual_messages_ids == mocked_message_ids


def test_mesh_message_calls_acknowledge_on_underlying_client_message():
    client_message = MagicMock()
    message = MeshMessage(client_message)

    message.acknowledge()

    client_message.acknowledge.assert_called_once()
