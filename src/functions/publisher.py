import logging
import time
from typing import Optional

from src.config import Config
from src.models import TaskModel
from src.models.models import TaskDeliveryModel
from src.utils import str_to_base64
from src.utils.ec import sign_message
from src.utils.task_manager import TaskManager
from src.waku import WakuClient

logger = logging.getLogger(__name__)


class Publisher:
    """
    Publisher class to handle task retrieval and processing.
    """

    def __init__(self, config: Config):
        self.config = config
        self.task_manager: Optional[TaskManager] = None
        self.waku: Optional[WakuClient] = None
        self._initialize_clients()

    def _initialize_clients(self):
        """
        Initialize the Task Manager and Waku client.
        """
        try:
            self.task_manager = TaskManager()
            logger.info("Task Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Task Manager: {e}", exc_info=True)

        try:
            self.waku = WakuClient()
            logger.info("Waku Client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Waku Client: {e}", exc_info=True)

    def _handle_available_tasks(self):
        """
        Handle task retrieval and processing if available.
        """

        try:
            task = self.task_manager.get_tasks()
            if task:
                logger.info(f"{len(task)} tasks retrieved, ready for processing.")
                task = TaskDeliveryModel(**task)
                task = self._publish_task(task)
                self.task_manager.add_aggregator_task(task)
            time.sleep(self.config.polling_interval)

        except Exception as e:
            logger.error(f"Failed to handle available tasks: {e}", exc_info=True)

    def _publish_task(self, task: TaskDeliveryModel):
        """
        Publishes a task to the topic specified in the configuration.

        Args:
            task (TaskDeliveryModel): Task data.

        Returns:
            TaskModel: Task data if successful, None otherwise.
        """
        if not self.waku:
            logger.warning("Waku client not initialized, skipping task publishing.")
            return

        try:
            task_model = TaskModel(
                taskId=task.id,
                filter=task.filter,
                input=task.prompt,
                deadline=int(time.time_ns() + 60 * 1000000000 * self.config.task_timeout_minute),
                publicKey=task.public_key if task.public_key[:2] != "0x" else task.public_key[2:],
            )
            task_json = task_model.json()
            signature = sign_message(self.config.dria_private_key, task_json)
            self.waku.push_content_topic(
                str_to_base64(signature.hex() + task_json),
                self.config.input_content_topic,
            )
            logger.info(f"Task published successfully: {task.id}")
            return task_model
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
