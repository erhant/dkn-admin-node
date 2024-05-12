import logging
import random
import uuid
from typing import List, Union

from fastbloom_rs import BloomFilter

from src.config import Config
from src.db import HollowClient
from src.dria import DriaClient
from src.models import NodeModel, TaskDeliveryModel, TaskModel, QuestionModel
from src.rabbit import Producer
from src.rabbit.consumer import Consumer

logger = logging.getLogger(__name__)


class TaskManager:
    """
    A class to manage tasks for the publisher service.
    """

    def __init__(self):
        self.consumer = Consumer()
        self.producer = Producer()
        self.config = Config()
        self.hollow = HollowClient()
        self.dria_client = DriaClient(self.config)

    def get_questions(self) -> Union[dict, None]:
        """
        Fetch available questions for delivery.

        Returns:
            dict: A question delivery models or None if no questions are available.
        """
        try:
            available_nodes = self.hollow.get("available-nodes-search")
            print("Available nodes: ", available_nodes)
            if not available_nodes:
                logger.warning("No available nodes found.")
                return None

            picked_nodes = random.choice(available_nodes)
            task = self.consumer.receive_message(self.config.SEARCH_CHANNEL, n=1)
            if not task:
                logger.warning("No question available for delivery.")
                return None

            bf = BloomFilter(len(picked_nodes), 0.01)
            for node in picked_nodes:
                bf.add(node)

            return QuestionModel(
                id=task["question_id"],
                question=task["question"],
            ).dict()

        except Exception as e:
            logger.error(f"An error occurred while fetching tasks: {e}")
            raise

    def get_tasks(self) -> Union[dict, None]:
        """
        Fetch available tasks for delivery.

        Returns:
            dict: A task delivery models or None if no tasks are available.
        """
        try:
            available_nodes = self.hollow.get("available-nodes")
            print("Available nodes: ", available_nodes)
            if not available_nodes:
                logger.warning("No available nodes found.")
                return None
            if len(available_nodes) < 3:
                available_nodes = available_nodes * 3
            picked_nodes = random.sample(
                available_nodes,
                max(3, self.config.compute_by_job),
            )
            task = self.consumer.receive_message(self.config.SYNTHESIS_CHANNEL, n=1)
            if not task:
                logger.warning("No task available for delivery.")
                return None

            bf = BloomFilter(len(picked_nodes), 0.01)
            for node in picked_nodes:
                bf.add(node)

            return TaskDeliveryModel(
                id=str(uuid.uuid4()),
                filter={"hex": bf.get_bytes().hex(), "hashes": bf.hashes()},
                prompt=task["prompt"],
                public_key=task["public_key"],
            ).dict()

        except Exception as e:
            logger.error(f"An error occurred while fetching tasks: {e}")
            raise

    def add_available_nodes(self, n: NodeModel) -> bool:
        """
        Add available nodes to the database.

        Args:
            n (NodeModel): Node model object containing the UUID and nodes.

        Returns:
            bool: True if the nodes were added successfully, False otherwise.
        """
        try:
            self.hollow.put("available-nodes", n.nodes)
            return True
        except Exception as e:
            logger.error(f"An error occurred while adding available nodes: {e}")
            return False

    def fetch_aggregation_tasks(self) -> Union[dict, None]:
        """
        Fetch aggregation tasks from the RabbitMQ channel.

        Returns:
            dict: An aggregation tasks or None if no tasks are available.
        """
        try:
            task = self.consumer.receive_message(self.config.AGGREGATION_CHANNEL, n=1)
            if not task:
                logger.warning("No aggregation tasks available.")
                return None
            return task
        except Exception as e:
            logger.error(f"An error occurred while fetching aggregation tasks: {e}")
            raise

    def fetch_search_tasks(self) -> Union[dict, None]:
        """
        Fetch search tasks from the RabbitMQ channel.

        Returns:
            dict: A search tasks or None if no tasks are available.
        """
        try:
            task = self.consumer.receive_message(self.config.SEARCH_CHANNEL, n=1)
            if not task:
                logger.warning("No search tasks available.")
                return None
            return task
        except Exception as e:
            logger.error(f"An error occurred while fetching search tasks: {e}")
            raise

    def add_aggregator_task(self, t: TaskModel) -> bool:
        """
        Add an aggregation task to the RabbitMQ channel and the database.

        Args:
            t (TaskModel): The aggregator task model.

        Returns:
            bool: True if the task was added successfully, False otherwise.
        """
        try:
            self.hollow.put(t.taskId, t.dict())
            self.producer.send_message(self.config.AGGREGATION_CHANNEL, t.json())
            self.hollow.update_key(t.taskId, "status", "published")
            return True
        except Exception as e:
            logger.error(f"An error occurred while adding an aggregation task: {e}")
            return False

    def add_search_results(self, task_id: str, context_answers: List[str], alignment_answers: List[str]) -> bool:
        """
        Add search results to the RabbitMQ.

        Args:
            task_id (str): The task ID.
            context_answers (List[str]): The context answers.
            alignment_answers (List[str]): The alignment answers.

        Returns:
            bool: True if the results were added successfully, False otherwise.

        """
        try:
            self.hollow.put(f"search-context-{task_id}", context_answers)
            self.hollow.put(f"search-alignment-{task_id}", alignment_answers)
            self.dria_client.trigger_task_generation(task_id)
        except Exception as e:
            logger.error(f"An error occurred while adding search results: {e}")
            return False
