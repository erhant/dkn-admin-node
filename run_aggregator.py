import logging
import time
from typing import Dict, Optional

from fastbloom_rs import BloomFilter

from src.config import Config
from src.dria_requests import DriaClient
from src.models import TaskModel
from src.utils.bert import BertEmbedding
from src.waku.waku_rest import WakuClient

logger = logging.getLogger(__name__)


class Aggregator:
    """
    Aggregator class to handle task retrieval and processing.
    """

    def __init__(self, config: Config):
        self.config = config
        self.dria_client = self._initialize_dria_client()
        self.waku = WakuClient()
        self.bert = BertEmbedding()
        self.bloom = BloomFilter(128, 0.01)

    @staticmethod
    def _initialize_dria_client() -> DriaClient:
        """Initialize Dria client with secret auth key.

        Returns:
            DriaClient: Dria client object.
        """
        try:
            client = DriaClient()
            logger.info("DRIA Client initialized successfully")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize DRIA Client: {e}")
            raise  # Raising to ensure failure in client initialization stops the process

    def run(self):
        """Continuously fetch and process tasks."""
        while True:
            try:
                task_id = self.dria_client.fetch_tasks()
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
                logger.error(f"Error during task fetching and processing: {e}")
                time.sleep(10)  # Sleep before retrying to ensure we don't hammer the system or service

    def process_task(self, task_data: TaskModel) -> Optional[Dict]:
        """Process an individual task.

        Args:
            task_data (TaskModel): Task data

        Returns:
            Optional[Dict]: Processed task output, or None if task processing failed
        """
        if task_data.timestamp < time.time():
            topic_results = self.waku.get_content_topic(f"/dria/2/{task_data.id}/proto")
            if len(topic_results) < self.config.compute_by_job:
                logger.warning("Task is not completed on given time.")
                return None

            bf_bytes = task_data.bloom_filter
            bloom = BloomFilter.from_bytes(bf_bytes, self.bloom.hashes())

            truthful_nodes = [result for result in topic_results if bloom.contains(result['node_id'])]

            if len(truthful_nodes) == self.config.compute_by_job:
                texts = [result['text'] for result in truthful_nodes]
                texts_embeddings = self.bert.generate_embeddings(texts)
                dists = [self.bert.maxsim(e.unsqueeze(0), texts_embeddings) for e in texts_embeddings]
                best_index = dists.index(max(dists))
                return truthful_nodes[best_index]
            else:
                logger.error("Node is not truthful.")
        else:
            logger.warning("Task timestamp is in the future.")
            return None
