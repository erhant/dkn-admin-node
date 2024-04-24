import logging
import time

from fastbloom_rs import BloomFilter

from src.config import config
from src.dria_requests import DriaClient
from src.models import TaskModel
from src.utils.bert import BertEmbedding
from src.waku.waku_rest import WakuClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Aggregator:
    """
    Aggregator class to handle task retrieval and processing.
    """

    def __init__(self):
        self.dria_client = self.initialize_dria_client()
        self.waku = WakuClient()
        self.bert = BertEmbedding()
        self.bloom = BloomFilter(128, 0.01)

    @staticmethod
    def initialize_dria_client() -> DriaClient:
        """Initialize Dria client with secret auth key.

        Returns:
            DriaClient: Dria client object.
        """
        try:
            client = DriaClient(auth=config.DRIA_AUTH_KEY)
            logging.info("DRIA Client initialized successfully")
            return client
        except Exception as e:
            logging.error(f"Failed to initialize DRIA Client: {e}")
            raise  # Raising to ensure failure in client initialization stops the process

    def fetch_and_process_tasks(self):
        """Continuously fetch and process tasks."""
        while True:
            try:
                task_id = self.dria_client.fetch_tasks()
                if task_id:
                    output = self.process_task(task_id)
                    if output:
                        logging.info(f"Task processed successfully: {output}")
                    else:
                        logging.error("Failed to process task properly.")
                else:
                    logging.warning("No available tasks")
                    time.sleep(10)  # Sleep to prevent tight loop if no tasks are available
            except Exception as e:
                logging.error(f"Error during task fetching and processing: {e}")
                time.sleep(10)  # Sleep before retrying to ensure we don't hammer the system or service

    def process_task(self, task_data: TaskModel):
        """Process an individual task.

        Args:
            task_data (TaskModel): Task ID

        Returns:
            dict: Processed task output
        """
        if task_data['timestamp'] < time.time():
            topic_results = self.waku.get_content_topic(f"/dria/2/{task_data['id']}/proto")
            if len(topic_results) < config.COMPUTE_BY_TASK:
                logging.warning("Task is not completed on given time.")
                return

            bf_bytes = task_data['bloom_filter']
            bloom = BloomFilter.from_bytes(bf_bytes, self.bloom.hashes())

            truthful_nodes = [result for result in topic_results if bloom.contains(result['node_id'])]

            if len(truthful_nodes) == config.COMPUTE_BY_TASK:
                texts = [result['text'] for result in truthful_nodes]
                texts_embeddings = self.bert.generate_embeddings(texts)
                dists = [self.bert.maxsim(e.unsqueeze(0), texts_embeddings) for e in texts_embeddings]
                best_index = dists.index(max(dists))
                return truthful_nodes[best_index]
            else:
                logging.error("Node is not truthful.")
        else:
            logging.warning("Task timestamp is in the future.")
            return None


if __name__ == "__main__":
    aggregator = Aggregator()
    aggregator.fetch_and_process_tasks()
