import sqlite3
import sys
import logging
from argparse import ArgumentParser

import boto3
from botocore.config import Config

from gp2gp.mesh.inbox import MeshInboxScanner
from gp2gp.mesh.file import MeshFileException
from gp2gp.registry import ProcessedFileRegistry
from gp2gp.uploader import MeshS3Uploader


class MeshToS3Synchronizer:
    def __init__(self, mesh_inbox_scanner, file_registry, file_uploader):
        self._mesh_inbox_scanner = mesh_inbox_scanner
        self._file_registry = file_registry
        self._file_uploader = file_uploader

    def run(self):
        mesh_files = self._mesh_inbox_scanner.scan()

        for file in mesh_files:
            if not self._file_registry.is_already_processed(file):
                try:
                    self._file_uploader.upload(file)
                    self._file_registry.mark_processed(file)
                except MeshFileException:
                    logging.error(f"Error uploading file: {file.path}", exc_info=True)


def parse_arguments(argument_list):
    parser = ArgumentParser(description="MESH to s3 synchronizer")
    parser.add_argument("--mesh-inbox", type=str)
    parser.add_argument("--s3-bucket", type=str)
    parser.add_argument("--state-file", type=str)
    parser.add_argument("--s3-endpoint-url", type=str)

    return parser.parse_args(argument_list)


def main():
    args = parse_arguments(sys.argv[1:])

    sqlite_conn = sqlite3.connect(args.state_file)
    s3 = boto3.client(
        "s3",
        endpoint_url=args.s3_endpoint_url,
        config=Config(signature_version="s3v4"),
    )

    mesh_inbox_scanner = MeshInboxScanner(args.mesh_inbox)
    file_registry = ProcessedFileRegistry(sqlite_conn)
    file_uploader = MeshS3Uploader(s3, args.s3_bucket)

    mesh_synchronizer = MeshToS3Synchronizer(mesh_inbox_scanner, file_registry, file_uploader)

    mesh_synchronizer.run()
