import logging
import time
from typing import Optional

from src.config import Config
from src.dria import DriaClient
from src.models import TaskModel
from src.models.models import TaskDeliveryModel
from src.utils import sign_address, str_to_base64
from src.waku import WakuClient

logger = logging.getLogger(__name__)


class Publisher:
    """
    Publisher class to handle task retrieval and processing.
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

    def _handle_available_tasks(self):
        """
        Handle task retrieval and processing if available.
        """
        if not self.dria_client:
            logger.warning("DRIA client not initialized, skipping task retrieval.")
            return

        try:
            tasks = self.dria_client.fetch_tasks()
            if tasks:
                logger.info(f"{len(tasks)} tasks retrieved, ready for processing.")
                for task in tasks:
                    task = TaskDeliveryModel(**task)
                    self._publish_task(task)
                    self.dria_client.add_tasks_to_queue(task.id)

        except Exception as e:
            logger.error(f"Failed to handle available tasks: {e}", exc_info=True)

    def _publish_task(self, task: TaskDeliveryModel):
        """
        Publishes a task to the topic specified in the configuration.

        Args:
            task (TaskDeliveryModel): Task data.
        """
        if not self.waku:
            logger.warning("Waku client not initialized, skipping task publishing.")
            return

        try:
            task_model = TaskModel(
                taskId=task.id,
                filter=task.filter,
                input=task.prompt,
                deadline=int(time.time_ns() + 60*1000000000 * self.config.task_timeout_minute),
                publicKey=task.pubKey,
            )
            task_json = task_model.json()
            signature = self._sign_message(self.config.dria_private_key, task_json)
            self.waku.push_content_topic(
                str_to_base64(signature.hex() + task_json),
                self.config.input_content_topic,
            )
            logger.info(f"Task published successfully: {task.id}")
        except Exception as e:
            logger.error(f"Failed to publish task: {e}", exc_info=True)

    def run(self):
        """
        Continuously checks for task availability and processes any found.
        """
        while True:
            try:
                self._handle_available_tasks()
            except Exception as e:
                logger.error(f"An error occurred while checking for tasks: {e}", exc_info=True)
            finally:
                time.sleep(self.config.polling_interval)
