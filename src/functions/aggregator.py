import logging
import time
from typing import Dict, Optional

from fastbloom_rs import BloomFilter

from src.config import Config
from src.dria import DriaClient
from src.models import TaskModel
from src.utils import BertEmbedding
from src.waku import WakuClient

logger = logging.getLogger(__name__)


class Aggregator:
    """
    Aggregator class to handle task retrieval and processing.
    """

    def __init__(self, config: Config):
        self.config = config
        self.dria_client: Optional[DriaClient] = None
        self.waku: Optional[WakuClient] = None
        self.bert: Optional[BertEmbedding] = None
        self.bloom: Optional[BloomFilter] = None
        self._initialize_components()

    def _initialize_components(self):
        """
        Initialize the required components (DRIA client, Waku client, Bert, and Bloom filter).
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
                task_id = self._fetch_task()
                if task_id:
                    output = self.process_task(task_id)
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

    def _fetch_task(self) -> Optional[TaskModel]:
        """
        Fetch task from the DRIA client.

        Returns:
            Optional[TaskModel]: Task data, or None if no tasks are available or the DRIA client is not initialized.
        """
        if not self.dria_client:
            logger.warning("DRIA client not initialized, skipping task fetching.")
            return None

        try:
            task_id = self.dria_client.fetch_aggregation_tasks()
            if task_id is None:
                return task_id
            logger.info(f"No tasks found")
        except Exception as e:
            logger.error(f"Error fetching tasks: {e}", exc_info=True)

        return None

    def process_task(self, task_data: TaskModel) -> Optional[Dict]:
        """Process an individual task.

        Args:
            task_data (TaskModel): Task data

        Returns:
            Optional[Dict]: Processed task output, or None if task processing failed
        """
        if not self.waku or not self.bert or not self.bloom:
            logger.warning("Required components not initialized, skipping task processing.")
            return None

        if task_data.timestamp < time.time():
            topic_results = self.waku.get_content_topic(f"/dria/2/{task_data.id}/proto")
            if len(topic_results) < self.config.compute_by_job:
                logger.warning("Task is not completed on given time.")
                return None

            try:
                bf_bytes = task_data.bloom_filter
                bloom = BloomFilter.from_bytes(bf_bytes, self.bloom.hashes())

                truthful_nodes = [
                    result for result in topic_results if bloom.contains(result["node_id"])
                ]

                if len(truthful_nodes) == self.config.compute_by_job:
                    texts = [result["text"] for result in truthful_nodes]
                    texts_embeddings = self.bert.generate_embeddings(texts)
                    dists = [
                        self.bert.maxsim(e.unsqueeze(0), texts_embeddings)
                        for e in texts_embeddings
                    ]
                    best_index = dists.index(max(dists))
                    return truthful_nodes[best_index]
                else:
                    logger.error("Node is not truthful.")
            except Exception as e:
                logger.error(f"Error processing task: {e}", exc_info=True)
        else:
            logger.warning("Task timestamp is in the future.")
            return None

        return None
