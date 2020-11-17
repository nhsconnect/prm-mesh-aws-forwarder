import sqlite3
import sys
import logging
import signal
from argparse import ArgumentParser
from threading import Event

import boto3
from botocore.config import Config

from gp2gp.mesh.inbox import MeshInboxScanner
from gp2gp.registry import ProcessedFileRegistry
from gp2gp.synchronizer import MeshToS3Synchronizer
from gp2gp.uploader import MeshS3Uploader

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

logger = logging.getLogger(__name__)


class SynchronizerService:
    def __init__(self, synchronizer, sleep_duration=10):
        self._synchronizer = synchronizer
        self._exit = Event()
        self._sleep_duration = sleep_duration

    def start(self):
        logger.info("Started synchronizer service")
        while not self._exit.is_set():
            self._synchronizer.synchronize()
            self._exit.wait(self._sleep_duration)
        logger.info("Exiting synchronizer service")

    def stop(self):
        logger.info("Received request to stop")
        self._exit.set()


def parse_arguments(argument_list):
    parser = ArgumentParser(description="MESH to s3 synchronizer")
    parser.add_argument("--mesh-inbox", type=str, required=True)
    parser.add_argument("--s3-bucket", type=str, required=True)
    parser.add_argument("--state-file", type=str, required=True)
    parser.add_argument("--s3-endpoint-url", type=str)

    return parser.parse_args(argument_list)


def main():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)

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
    synchronizer_service = SynchronizerService(mesh_synchronizer)

    def handle_sigterm(signum, frame):
        synchronizer_service.stop()

    signal.signal(signal.SIGINT, handle_sigterm)
    signal.signal(signal.SIGTERM, handle_sigterm)

    synchronizer_service.start()
