from pathlib import Path

from gp2gp.synchronizer import MeshToS3Synchronizer
from gp2gp.mesh.file import MeshFile, MeshFileException
from unittest.mock import MagicMock, call


def test_uploads_file():
    mock_mesh_inbox_scanner = MagicMock()
    mock_file_registry = MagicMock()
    mock_file_uploader = MagicMock()

    mock_mesh_file = MeshFile(Path("path/to/file.dat"))

    mock_mesh_inbox_scanner.scan.return_value = [mock_mesh_file]
    mock_file_registry.is_already_processed.return_value = False

    uploader = MeshToS3Synchronizer(mock_mesh_inbox_scanner, mock_file_registry, mock_file_uploader)

    uploader.run()

    mock_file_uploader.upload.assert_called_once_with(mock_mesh_file)


def test_uploads_multiple_files():
    mock_mesh_inbox_scanner = MagicMock()
    mock_file_registry = MagicMock()
    mock_file_uploader = MagicMock()

    mock_mesh_file = MeshFile(path=Path("path/to/file.dat"))
    mock_second_mesh_file = MeshFile(path=Path("path/to/secondfile.dat"))

    mock_mesh_inbox_scanner.scan.return_value = [mock_mesh_file, mock_second_mesh_file]
    mock_file_registry.is_already_processed.return_value = False

    uploader = MeshToS3Synchronizer(mock_mesh_inbox_scanner, mock_file_registry, mock_file_uploader)

    uploader.run()

    calls = [call(mock_mesh_file), call(mock_second_mesh_file)]
    mock_file_uploader.upload.assert_has_calls(calls)


class MockFileRegistry:
    def __init__(self):
        self.registry = set()

    def mark_processed(self, mesh_file):
        self.registry.add(mesh_file.path)

    def is_already_processed(self, mesh_file):
        return mesh_file.path in self.registry


def mock_registry(already_processed):
    mock_file_registry = MockFileRegistry()

    for filename in already_processed:
        mock_file_registry.mark_processed(filename)

    return mock_file_registry


def test_only_uploads_new_files():

    mock_new_file = MeshFile(path=Path("path/to/newfile.dat"))
    mock_old_file = MeshFile(path=Path("path/to/oldfile.dat"))

    mock_mesh_inbox_scanner = MagicMock()
    mock_file_registry = mock_registry(already_processed=[mock_old_file])
    mock_file_uploader = MagicMock()

    mock_mesh_inbox_scanner.scan.return_value = [mock_new_file, mock_old_file]

    uploader = MeshToS3Synchronizer(mock_mesh_inbox_scanner, mock_file_registry, mock_file_uploader)

    uploader.run()

    mock_file_uploader.upload.assert_called_once_with(MeshFile(path=Path("path/to/newfile.dat")))


def test_uploads_file_only_once():

    mock_mesh_inbox_scanner = MagicMock()
    mock_file_registry = MockFileRegistry()
    mock_file_uploader = MagicMock()

    mock_mesh_file = MeshFile(path=Path("path/to/file.dat"))

    mock_mesh_inbox_scanner.scan.return_value = [mock_mesh_file]

    uploader = MeshToS3Synchronizer(mock_mesh_inbox_scanner, mock_file_registry, mock_file_uploader)

    uploader.run()
    uploader.run()

    mock_file_uploader.upload.assert_called_once_with(mock_mesh_file)


def test_does_not_fail_when_mesh_file_exception_is_thrown():

    mock_mesh_inbox_scanner = MagicMock()
    mock_file_registry = MockFileRegistry()
    mock_file_uploader = MagicMock()

    mock_mesh_file_1 = MeshFile(path=Path("path/to/file1.dat"))
    mock_mesh_file_2 = MeshFile(path=Path("path/to/file2.dat"))
    mock_mesh_file_3 = MeshFile(path=Path("path/to/file3.dat"))

    mock_mesh_inbox_scanner.scan.return_value = [
        mock_mesh_file_1,
        mock_mesh_file_2,
        mock_mesh_file_3,
    ]
    mock_file_uploader.upload.side_effect = [None, MeshFileException(), None]

    uploader = MeshToS3Synchronizer(mock_mesh_inbox_scanner, mock_file_registry, mock_file_uploader)

    uploader.run()

    calls = [call(mock_mesh_file_1), call(mock_mesh_file_2), call(mock_mesh_file_3)]
    mock_file_uploader.upload.assert_has_calls(calls)
