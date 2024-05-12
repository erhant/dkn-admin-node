import base64
import json
import logging
import time
from typing import Optional, Dict

from src.config import Config
from src.models.models import SearchTaskModel
from src.utils.ec import decrypt_message, recover_public_key, publickey_to_address
from src.utils.task_manager import TaskManager
from src.waku import WakuClient

logger = logging.getLogger(__name__)


class SearchAggregator:
    def __init__(self):
        self.config = Config()
        self.waku: Optional[WakuClient] = None
        self.task_manager: Optional[TaskManager] = None

    def _initialize_clients(self):
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
        while True:
            try:
                task = self._fetch_queries()
                if task:
                    output = self.process_task(SearchTaskModel(**task))
                    if output:
                        logger.info(f"Task processed successfully: {output}")
                    else:
                        logger.error("Failed to process task properly.")
                else:
                    logger.warning("No available tasks")
                    time.sleep(10)
            except Exception as e:
                logger.error(f"Error during task fetching and processing: {e}", exc_info=True)
                time.sleep(10)

    def _fetch_queries(self) -> Optional[dict]:
        try:
            return self.task_manager.fetch_search_tasks()
        except Exception as e:
            logger.error(f"An error occurred while fetching tasks: {e}")
            raise

    def process_task(self, task_data: SearchTaskModel) -> Optional[Dict]:
        if not all([self.waku]):
            logger.warning("Required components not initialized, skipping task processing.")
            return None

        if task_data.timestamp < time.time():
            topic_results = self.waku.get_content_topic(f"/dria/0/{task_data.task_id}/proto")
            if not topic_results:
                logger.warning("No topic results found for the task.")
                return None

            try:
                for topic_result in topic_results:
                    topic_result_data = json.loads(base64.b64decode(topic_result["payload"]).decode("utf-8"))
                    result = decrypt_message(task_data.privateKey, topic_result_data["ciphertext"])
                    public_key = recover_public_key(topic_result_data["signature"],
                                                    bytes.fromhex(result))
                    address = publickey_to_address(public_key)

                    truthful_nodes = [
                        result for result in topic_results if address in task_data.nodes
                    ]

                    if len(truthful_nodes) > 0:
                        logger.info(f"Found {len(truthful_nodes)} truthful nodes to process the task.")
                        texts = [json.loads(base64.b64decode(result["payload"]).decode("utf-8"))["text"] for result in
                                 truthful_nodes]

                        context_answers = []
                        alignments = []
                        for i in texts:
                            if i["type"] == "context":
                                context_answers.append(i["text"])
                            elif i["type"] == "alignment":
                                alignments.append(i["text"])
                            else:
                                logger.warning(f"Unknown type: {i['type']}")
                        self.task_manager.add_search_results(task_data.task_id, context_answers, alignments)
                    else:
                        logger.error("Not enough truthful nodes found to process the task.")
            except Exception as e:
                logger.error(f"Error processing task: {e}", exc_info=True)
        else:
            logger.warning("Task timestamp is in the future, skipping task processing.")

        return None
