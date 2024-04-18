import base64
import json
import logging
import time
import uuid

from src.config import config
from src.dria_requests import DriaClient
from src.utils.messaging_utils import json_to_base64, base64_to_json
from src.waku.waku_rest import WakuClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Monitor:
    """
    Monitor class to handle the monitoring of the node network.
    """

    def __init__(self):
        self.dria_client = self.initialize_client()
        self.waku = WakuClient()

    @staticmethod
    def initialize_client():
        """
        Initialize the DRIA client with the secret authentication key.

        Returns:
            DriaClient: Initialized DRIA client object.
        """
        try:
            client = DriaClient(auth=config.NODE_AUTH_KEY)
            logging.info("DRIA Client initialized successfully")
            return client
        except Exception as e:
            logging.error(f"Failed to initialize DRIA Client: {e}")
            return None

    def heartbeat(self):
        """
        Periodically sends a heartbeat to the node network and checks for responses.

        Returns:
            None
        """
        while True:
            uuid_ = str(uuid.uuid4())
            try:
                if not self.send_heartbeat(uuid_):
                    time.sleep(config.POLLING_INTERVAL)  # Short wait before retrying to send heartbeat
                    continue

                time.sleep(config.MONITORING_INTERVAL)  # Wait configured monitoring interval

                if self.check_heartbeat(uuid_):
                    logging.info(f"Received heartbeat response for: {uuid_}")
                else:
                    logging.error(f"No response received for: {uuid_}")

            except Exception as e:
                logging.error(f"Error during heartbeat process: {e}")
                time.sleep(config.POLLING_INTERVAL)  # Wait before retrying the entire process

    def send_heartbeat(self, uuid_):
        """
        Sends a heartbeat message to the network.

        Args:
            uuid_ (str): The unique identifier for the heartbeat.

        Returns:
            bool: True if successful, False otherwise.
        """
        status = self.waku.push_content_topic(json_to_base64({"message": uuid_}),
                                              "/dria/2/heartbeat/proto")
        if not status:
            logging.error(f"Failed to send heartbeat: {uuid_}")
            return False

        logging.info(f"Sent heartbeat: {uuid_}")
        return True

    def check_heartbeat(self, uuid_):
        """
        Checks for a response to a previously sent heartbeat.

        Args:
            uuid_ (str): The unique identifier for the heartbeat.

        Returns:
            bool: True if a response is received, False otherwise.
        """
        topic = self.waku.get_content_topic(f"/dria/2/{uuid}/proto")
        if topic:
            self.dria_client.add_available_nodes(base64_to_json(topic))
            return True
        logging.error(f"Failed to receive heartbeat response: {uuid_}")
        return False


if __name__ == "__main__":
    monitor = Monitor()
    monitor.heartbeat()
