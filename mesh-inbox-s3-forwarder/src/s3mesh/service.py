from s3mesh.forwarder import MeshToS3Forwarder
import logging
from threading import Event

logger = logging.getLogger(__name__)


class MeshToS3ForwarderService:
    def __init__(self, forwarder: MeshToS3Forwarder, poll_frequency_sec: int):
        self._forwarder = forwarder
        self._exit = Event()
        self._poll_frequency_sec = poll_frequency_sec

    def start(self):
        logger.info("Started forwarder service")
        while not self._exit.is_set():
            self._forwarder.forward_messages()
            self._exit.wait(self._poll_frequency_sec)
        logger.info("Exiting forwarder service")

    def stop(self):
        logger.info("Received request to stop")
        self._exit.set()
