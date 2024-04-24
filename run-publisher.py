import logging
import time

from src.config import config
from src.dria_requests import DriaClient
from src.models import TaskModel
from src.utils.ec import sign_address
from src.utils.messaging_utils import task_to_base64
from src.waku.waku_rest import WakuClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Publisher:
    """
    Publisher class to handle task retrieval and processing.
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
    def sign_message(task) -> str:
        """
        Sign task using a private key.

        Returns:
            str: Signature string.
        """
        try:
            return sign_address(config.DRIA_PRIVATE_KEY, task)
        except Exception as e:
            logging.error(f"Error signing message: {e}")
            return ""

    def handle_available_tasks(self):
        """
        Handle task retrieval and processing if available.

        Returns:
            None
        """

        try:
            tasks = self.dria_client.fetch_tasks()
            if tasks:
                logging.info(f"{len(tasks)} tasks retrieved, ready for processing.")
                for task in tasks:
                    self.publish_task(task)
            else:
                logging.warning("No available tasks after retrieval attempt.")
        except Exception as e:
            logging.error(f"Failed to handle available tasks: {e}")

    def publish_task(self, task: dict):
        """
        Publishes a task to the topic specified in the configuration.

        Args:
            task (dict): Task data.

        Returns:
            None
        """
        try:
            task = TaskModel(**{
                "taskId": task["id"],
                "filter": task["filter"],
                "prompt": task["prompt"],
                "deadline": time.time() + 60 * config.TASK_TIMEOUT_MINUTE,
                "pubKey": task["pubKey"],
            }).json()
            signature = self.sign_message(task)
            self.waku.push_content_topic(task_to_base64(signature, signature), config.INPUT_CONTENT_TOPIC)
        except Exception as e:
            logging.error(f"Failed to publish task: {e}")

    def check_and_publish_tasks(self):
        """
        Continuously checks for task availability and processes any found.
        """
        while True:
            try:
                self.handle_available_tasks()
            except Exception as e:
                logging.error(f"An error occurred while checking for tasks: {e}")
            finally:
                time.sleep(config.POLLING_INTERVAL)


if __name__ == "__main__":
    publisher = Publisher()
    if publisher.dria_client:
        publisher.check_and_publish_tasks()
