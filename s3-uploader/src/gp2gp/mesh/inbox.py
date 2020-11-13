from pathlib import Path

from gp2gp.mesh.file import MeshFile


class MeshInboxScanner:
    def __init__(self, directory):
        self._directory = Path(directory)

    def scan(self):
        file_paths = self._directory.glob("*.dat")

        for file_path in file_paths:
            yield MeshFile(path=file_path)
