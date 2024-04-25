import json
import logging
import time
import uuid

import sha3

from src.config import config
from src.dria_requests import DriaClient
from src.utils.ec import recover_public_key, sign_address
from src.utils.messaging_utils import str_to_base64, base64_to_json
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
    def sign_message(uuid_) -> bytes:
        """
        Sign uuid using a private key.

        Returns:
            str: Signature string.
        """
        try:
            return sign_address(config.DRIA_PRIVATE_KEY, uuid_)
        except Exception as e:
            logging.error(f"Error signing message: {e}")
            raise

    @staticmethod
    def initialize_client() -> DriaClient:
        """
        Initialize the DRIA client with the secret authentication key.

        Returns:
            DriaClient: Initialized DRIA client object.
        """
        try:
            client = DriaClient()
            logging.info("DRIA Client initialized successfully")
            return client
        except Exception as e:
            logging.error(f"Failed to initialize DRIA Client: {e}")
            raise  # Raising to ensure failure in client initialization stops the process

    def run(self):
        """
        Periodically sends a heartbeat to the node network and checks for responses.

        Returns:
            None
        """
        while True:
            uuid_ = str(uuid.uuid4())
            payload = json.dumps({"uuid": uuid_})
            signed_uuid = self.sign_message(payload)
            try:
                if not self.send_heartbeat(payload, signed_uuid.hex()):
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

    def send_heartbeat(self, payload: str, sign: str) -> bool:
        """
        Sends a heartbeat message to the network.

        Args:
            payload (str): The unique identifier for the heartbeat.
            sign (str): The signature of the payload.

        Returns:
            bool: True if successful, False otherwise.
        """
        status = self.waku.push_content_topic(str_to_base64(sign+payload),
                                              "/dria/0/heartbeat/proto")
        if not status:
            logging.error(f"Failed to send heartbeat: {payload}")
            return False

        logging.info(f"Sent heartbeat: {payload}")
        return True

    def check_heartbeat(self, uuid_: str) -> bool:
        """
        Checks for a response to a previously sent heartbeat.

        Args:
            uuid_ (str): The unique identifier for the heartbeat.

        Returns:
            bool: True if a response is received, False otherwise.
        """
        topic = self.waku.get_content_topic(f"/dria/0/{uuid_}/proto")
        if topic:
            nodes_as_address = self.decrypt_nodes(topic, json.dumps({"uuid": uuid_}))
            self.dria_client.add_available_nodes(base64_to_json(nodes_as_address))
            return True
        logging.error(f"Failed to receive heartbeat response: {uuid_}")
        return False

    @staticmethod
    def decrypt_nodes(available_nodes: list, msg: str) -> list:
        """
        Decrypts the available nodes to get the address.

        Args:
            available_nodes (list): Encrypted node identifiers.
            msg: (str): Message to decrypt the heartbeat results.

        Returns:
            list: List of decrypted node addresses.
        """
        node_address = []
        for node in available_nodes:
            try:
                public_key = recover_public_key(node, msg)
                address = sha3.keccak_256(public_key[2:]).digest()[-20:].hex()
                node_address.append(address)
            except Exception as e:
                logging.error(f"Failed to decrypt node: {e}")
        return node_address
