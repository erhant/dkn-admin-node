import logging
import time

import sha3
from fastbloom_rs import BloomFilter

from src.config import config
from src.dria_requests import DriaClient
from src.models import PublishModel
from src.utils.ec import recover_public_key, sign_address
from src.utils.messaging_utils import job_to_base64
from src.waku.waku_rest import WakuClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Publisher:
    """
    Publisher class to handle job retrieval and processing.
    """

    def __init__(self):
        self.dria_client = self.initialize_client()
        self.waku = WakuClient()

    @staticmethod
    def initialize_client() -> DriaClient:
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
            raise

    @staticmethod
    def sign_message(job) -> str:
        """
        Siga job using a private key.

        Returns:
            str: Signature string.
        """
        try:
            return sign_address(config.DRIA_PRIVATE_KEY, job)
        except Exception as e:
            logging.error(f"Error signing message: {e}")
            return ""

    def handle_available_jobs(self, available_nodes: list):
        """
        Handle job retrieval and processing if available.

        Args:
            available_nodes (list): List of available node addresses.

        Returns:
            None
        """
        bf = BloomFilter(128, 0.01)
        for node in available_nodes:
            bf.add(node)

        try:
            jobs = self.dria_client.get_jobs()
            if jobs:
                logging.info(f"{len(jobs)} jobs retrieved, ready for processing.")
                for job in jobs:
                    self.publish_job(job, bf)
            else:
                logging.warning("No available jobs after retrieval attempt.")
        except Exception as e:
            logging.error(f"Failed to handle available jobs: {e}")

    def publish_job(self, job: dict, bf: BloomFilter):
        """
        Publishes a job to the topic specified in the configuration.

        Args:
            job (dict): Job data.
            bf (Bloom): Bloom filter with node addresses.

        Returns:
            None
        """
        try:
            job = PublishModel(**{
                "jobId": job["id"],
                "filter": {"hex": bf.get_bytes(), "hashes": bf.hashes()},
                "prompt": job["prompt"],
                "deadline": time.time() + 60 * config.JOB_TIMEOUT_MINUTE,
                "pubKey": job["pubKey"],
            }).json()
            signature = self.sign_message(job)
            self.waku.push_content_topic(job_to_base64(signature, signature), config.INPUT_CONTENT_TOPIC)
        except Exception as e:
            logging.error(f"Failed to publish job: {e}")

    def check_and_publish_jobs(self):
        """
        Continuously checks for job availability and processes any found.
        """
        while True:
            try:
                available_nodes = self.dria_client.get_available_nodes()
                if available_nodes:
                    nodes_as_address = self.decrypt_nodes(available_nodes)
                    self.handle_available_jobs(nodes_as_address)
                else:
                    logging.info("No available nodes currently.")
            except Exception as e:
                logging.error(f"An error occurred while checking for jobs: {e}")
            finally:
                time.sleep(config.POLLING_INTERVAL)

    @staticmethod
    def decrypt_nodes(available_nodes: list) -> list:
        """
        Decrypts the available nodes to get the address.

        Args:
            available_nodes (list): Encrypted node identifiers.

        Returns:
            list: List of decrypted node addresses.
        """
        node_address = []
        for node in available_nodes:
            try:
                public_key = recover_public_key(node, config.AVAILABLE_MESSAGE)
                address = sha3.keccak_256(public_key[2:]).digest()[-20:].hex()
                node_address.append(address)
            except Exception as e:
                logging.error(f"Failed to decrypt node: {e}")
        return node_address


if __name__ == "__main__":
    publisher = Publisher()
    if publisher.dria_client and publisher.signature:
        publisher.check_and_publish_jobs()
