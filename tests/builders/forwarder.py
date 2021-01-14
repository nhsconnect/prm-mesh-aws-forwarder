from unittest.mock import MagicMock

from s3mesh.forwarder import MeshToS3Forwarder


def build_forwarder(**kwargs):
    mock_mesh_inbox = kwargs.get("mesh_inbox", MagicMock())
    mock_s3_uploader = kwargs.get("s3_uploader", MagicMock())
    mock_probe = kwargs.get("probe", MagicMock())
    mock_mesh_inbox.read_messages.return_value = kwargs.get("incoming_messages", [])
    mock_mesh_inbox.read_messages.side_effect = kwargs.get("read_error", None)
    mock_mesh_inbox.count_messages.side_effect = kwargs.get("count_error", None)
    mock_mesh_inbox.count_messages.return_value = kwargs.get("inbox_message_count", 0)

    return MeshToS3Forwarder(mock_mesh_inbox, mock_s3_uploader, mock_probe)
