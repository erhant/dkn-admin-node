import logging
import time

from src.config import Config
from src.dria import DriaClient
from src.models import TaskModel
from src.utils import sign_address, str_to_base64
from src.waku import WakuClient

logger = logging.getLogger(__name__)


class Publisher:
    """
    Publisher class to handle task retrieval and processing.
    """

    def __init__(self, config: Config):
        self.config = config
        self.dria_client = self._initialize_client()
        self.waku = WakuClient()

    def _initialize_client(self) -> DriaClient:
        """
        Initialize the DRIA client with the secret authentication key.

        Returns:
            DriaClient: Initialized DRIA client object.
        """
        try:
            client = DriaClient(self.config)
            logger.info("DRIA Client initialized successfully")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize DRIA Client: {e}")
            raise

    @staticmethod
    def _sign_message(private_key: str, message: str) -> bytes:
        """
        Sign a message using the provided private key.

        Args:
            private_key (str): The private key to use for signing.
            message (str): The message to sign.

        Returns:
            bytes: The signature of the message.
        """
        try:
            return sign_address(private_key, message)
        except Exception as e:
            logger.error(f"Error signing message: {e}")
            raise e

    def _handle_available_tasks(self):
        """
        Handle task retrieval and processing if available.
        """
        try:
            tasks = self.dria_client.fetch_tasks()
            if tasks:
                logger.info(f"{len(tasks)} tasks retrieved, ready for processing.")
                for task in tasks:
                    self._publish_task(task)
        except Exception as e:
            logger.error(f"Failed to handle available tasks: {e}")

    def _publish_task(self, task: dict):
        """
        Publishes a task to the topic specified in the configuration.

        Args:
            task (dict): Task data.
        """
        try:
            task_model = TaskModel(
                task_id=task["id"],
                bloom_filter=task["filter"],
                prompt=task["prompt"],
                deadline=time.time() + 60 * self.config.task_timeout_minute,
                public_key=task["pubKey"],
            )
            task_json = task_model.json()
            signature = self._sign_message(self.config.dria_private_key, task_json)
            self.waku.push_content_topic(str_to_base64(signature.hex() + task_json), self.config.input_content_topic)
        except Exception as e:
            logger.error(f"Failed to publish task: {e}")

    def run(self):
        """
        Continuously checks for task availability and processes any found.
        """
        while True:
            try:
                self._handle_available_tasks()
            except Exception as e:
                logger.error(f"An error occurred while checking for tasks: {e}")
            finally:
                time.sleep(self.config.polling_interval)
