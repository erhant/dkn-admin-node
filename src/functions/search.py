import json
import logging
from typing import Optional

from src.config import Config
from src.utils import str_to_base64
from src.utils.ec import sign_message
from src.utils.task_manager import TaskManager
from src.waku import WakuClient

logger = logging.getLogger(__name__)


class Search:
    """
    This class is used to interact with the Dria API for research purposes.

    """

    def __init__(self):
        self.config = Config()
        self.waku: Optional[WakuClient] = None
        self.task_manager: Optional[TaskManager] = None

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

    def run(self):
        """
        Run the search process.

        """

        try:
            self._initialize_clients()
            logger.info("Search process started")
            while True:
                task = self.task_manager.get_questions()
                if task:
                    logger.info(f"Task received: {task}")
                    task_json = json.dumps(task, ensure_ascii=False)
                    signature = sign_message(self.config.dria_private_key, task_json)
                    self.waku.push_content_topic(
                        str_to_base64(signature.hex() + task_json),
                        self.config.search_content_topic,
                    )
                else:
                    logger.warning("No available tasks")
        except Exception as e:
            logger.error(f"An error occurred while running the search process: {e}")
            raise
