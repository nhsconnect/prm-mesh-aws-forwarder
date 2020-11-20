import logging
from gp2gp.mesh.file import MeshFileException

logger = logging.getLogger(__name__)


class MeshToS3Synchronizer:
    def __init__(self, mesh_inbox_scanner, file_registry, file_uploader):
        self._mesh_inbox_scanner = mesh_inbox_scanner
        self._file_registry = file_registry
        self._file_uploader = file_uploader

    def synchronize(self):
        mesh_files = self._mesh_inbox_scanner.scan()

        for file in mesh_files:
            if not self._file_registry.is_already_processed(file):
                try:
                    logger.info(f"Synchronizing {file.path}")
                    self._file_uploader.upload(file)
                    self._file_registry.mark_processed(file)
                except MeshFileException:
                    logger.error(f"Error uploading file: {file.path}", exc_info=True)
