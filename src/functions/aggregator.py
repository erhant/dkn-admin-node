import base64
import json
import logging
import time
from typing import Dict, Optional, List

from fastbloom_rs import BloomFilter

from src.config import Config
from src.models import AggregatorTaskModel
from src.utils import BertEmbedding
from src.utils.ec import decrypt_message, recover_public_key, publickey_to_address
from src.utils.task_manager import TaskManager
from src.waku import WakuClient

logger = logging.getLogger(__name__)


class Aggregator:
    """
    Aggregator class to handle task retrieval and processing.
    """

    def __init__(self, config: Config):
        self.config = config
        self.task_manager: Optional[TaskManager] = None
        self.waku: Optional[WakuClient] = None
        self.bert: Optional[BertEmbedding] = None
        self.bloom: Optional[BloomFilter] = None
        self._initialize_components()

    def _initialize_components(self):
        """
        Initialize the required components (Task Manager, Waku client, Bert, and Bloom filter).
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

        try:
            self.bert = BertEmbedding()
            logger.info("Bert Embedding initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Bert Embedding: {e}", exc_info=True)

        try:
            self.bloom = BloomFilter(128, 0.01)
            logger.info("Bloom Filter initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Bloom Filter: {e}", exc_info=True)

    def run(self):
        """Continuously fetch and process tasks."""
        while True:
            try:
                task = self._fetch_task()
                if task:
                    output = self.process_task(AggregatorTaskModel(**task))
                    if output:
                        logger.info(f"Task processed successfully: {output}")
                    else:
                        logger.error("Failed to process task properly.")
                else:
                    logger.warning("No available tasks")
                    time.sleep(10)  # Sleep to prevent tight loop if no tasks are available
            except Exception as e:
                logger.error(f"Error during task fetching and processing: {e}", exc_info=True)
                time.sleep(10)  # Sleep before retrying to ensure we don't hammer the system or service

    def _fetch_task(self) -> Optional[dict]:
        """
        Fetch task from the Task Manager.

        Returns:
            Optional[Dict]: Task data, or None if no tasks are available or the Task Manager is not initialized.
        """
        if self.task_manager is None:
            logger.warning("Task Manager is not initialized, cannot fetch tasks.")
            return None

        try:
            task = self.task_manager.fetch_aggregation_tasks()
            if task is not None:
                return task
            logger.info(f"No tasks found")
        except Exception as e:
            logger.error(f"Error fetching tasks: {e}", exc_info=True)

        return None

    def process_task(self, task_data: AggregatorTaskModel) -> Optional[Dict]:
        """Process an individual task.

        Args:
            task_data (AggregatorTaskModel): Task data

        Returns:
            Optional[Dict]: Processed task output, or None if task processing failed
        """
        if not all([self.waku, self.bert, self.bloom]):
            logger.warning("Required components not initialized, skipping task processing.")
            return None

        if task_data.timestamp < time.time():
            topic_results = self.waku.get_content_topic(f"/dria/0/{task_data.taskId}/proto")
            if not topic_results:
                logger.warning("No topic results found for the task.")
                return None

            bf_bytes = task_data.filter

            try:
                for topic_result in topic_results:
                    topic_result_data = json.loads(base64.b64decode(topic_result["payload"]).decode("utf-8"))
                    result = decrypt_message(task_data.privateKey, topic_result_data["ciphertext"])
                    public_key = recover_public_key(topic_result_data["signature"],
                                                    bytes.fromhex(result))
                    address = publickey_to_address(public_key)

                    bloom = BloomFilter.from_bytes(bf_bytes.hex.encode("utf-8"), self.bloom.hashes())

                    truthful_nodes = [
                        result for result in topic_results if bloom.contains(address)
                    ]

                    if len(truthful_nodes) == self.config.compute_by_job:
                        texts = [json.loads(base64.b64decode(result["payload"]).decode("utf-8"))["text"] for result in
                                 truthful_nodes]
                        texts_embeddings = self.bert.generate_embeddings(texts)
                        dists = [
                            self.bert.maxsim(e.unsqueeze(0), texts_embeddings)
                            for e in texts_embeddings
                        ]
                        best_index = dists.index(max(dists))
                        return truthful_nodes[best_index]
                    else:
                        logger.error("Not enough truthful nodes found to process the task.")
            except Exception as e:
                logger.error(f"Error processing task: {e}", exc_info=True)
        else:
            logger.warning("Task timestamp is in the future, skipping task processing.")

        return None
