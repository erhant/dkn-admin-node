import json
import logging
import time
import uuid
from typing import List, Optional

import sha3

from src.config import Config
from src.dria import DriaClient
from src.utils import (
    recover_public_key,
    sign_address,
    uncompressed_public_key,
    str_to_base64,
    base64_to_json,
)
from src.waku import WakuClient

logger = logging.getLogger(__name__)


class Monitor:
    """
    Monitor class to handle the monitoring of the node network.
    """

    def __init__(self, config: Config):
        self.config = config
        self.dria_client: Optional[DriaClient] = None
        self.waku: Optional[WakuClient] = None
        self._initialize_clients()

    def _initialize_clients(self):
        """
        Initialize the DRIA client and Waku client.
        """
        try:
            self.dria_client = DriaClient(self.config)
            logger.info("DRIA Client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DRIA Client: {e}", exc_info=True)

        try:
            self.waku = WakuClient()
            logger.info("Waku Client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Waku Client: {e}", exc_info=True)

    @staticmethod
    def _sign_message(private_key: str, message: str) -> bytes:
        """
        Sign a message using the provided private key.

        Args:
            private_key (str): The private key to use for signing.
            message (str): The message to sign.

        Returns:
            bytes: The signature of the message.

        Raises:
            Exception: If there is an error signing the message.
        """
        try:
            return sign_address(private_key, message)
        except Exception as e:
            logger.error(f"Error signing message: {e}", exc_info=True)
            raise e

    def run(self):
        """
        Periodically sends a heartbeat to the node network and checks for responses.
        """
        while True:
            uuid_ = str(uuid.uuid4())
            payload = json.dumps(
                {
                    "uuid": uuid_,
                    "deadline": int(time.time() + self.config.monitoring_interval),
                }
            )
            try:
                signed_uuid = self._sign_message(self.config.dria_private_key, payload)
            except Exception as e:
                logger.error(f"Error signing heartbeat payload: {e}", exc_info=True)
                time.sleep(self.config.polling_interval)
                continue

            try:
                if not self._send_heartbeat(payload, signed_uuid.hex()):
                    time.sleep(self.config.polling_interval)
                    continue

                time.sleep(self.config.monitoring_interval)

                if self._check_heartbeat(uuid_):
                    logger.info(f"Received heartbeat response for: {uuid_}")
                else:
                    logger.error(f"No response received for: {uuid_}")

            except Exception as e:
                logger.error(f"Error during heartbeat process: {e}", exc_info=True)
                time.sleep(self.config.polling_interval)

    def _send_heartbeat(self, payload: str, signature: str) -> bool:
        """
        Sends a heartbeat message to the network.

        Args:
            payload (str): The unique identifier for the heartbeat.
            signature (str): The signature of the payload.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.waku:
            logger.warning("Waku client not initialized, skipping heartbeat sending.")
            return False

        status = self.waku.push_content_topic(
            str_to_base64(signature + payload), self.config.heartbeat_topic
        )
        if not status:
            logger.error(f"Failed to send heartbeat: {payload}")
            return False

        logger.info(f"Sent heartbeat: {payload}")
        return True

    def _check_heartbeat(self, uuid_: str) -> bool:
        """
        Checks for a response to a previously sent heartbeat.

        Args:
            uuid_ (str): The unique identifier for the heartbeat.

        Returns:
            bool: True if a response is received, False otherwise.
        """
        if not self.waku:
            logger.warning("Waku client not initialized, skipping heartbeat checking.")
            return False

        topic = self.waku.get_content_topic(f"/dria/0/{uuid_}/proto")
        if topic:
            try:
                nodes_as_address = self._decrypt_nodes(
                    [base64_to_json(t["payload"]) for t in topic], uuid_
                )
                if self.dria_client:
                    self.dria_client.add_available_nodes(nodes_as_address)
                else:
                    logger.warning("DRIA client not initialized, skipping node addition.")
                return True
            except Exception as e:
                logger.error(f"Error processing heartbeat response: {e}", exc_info=True)

        logger.error(f"Failed to receive heartbeat response: {uuid_}")
        return False

    @staticmethod
    def _decrypt_nodes(available_nodes: List[str], msg: str) -> List[str]:
        """
        Decrypts the available nodes to get the address.

        Args:
            available_nodes (List[str]): Encrypted node identifiers.
            msg (str): Message to decrypt the heartbeat results.

        Returns:
            List[str]: List of decrypted node addresses.
        """
        node_addresses = []
        for node in available_nodes:
            try:
                public_key = recover_public_key(bytes.fromhex(node), msg)
                public_key = uncompressed_public_key(public_key)
                address = sha3.keccak_256(public_key[1:]).digest()[-20:].hex()
                node_addresses.append(address)
            except Exception as e:
                logger.error(f"Failed to decrypt node: {e}", exc_info=True)
        return node_addresses
