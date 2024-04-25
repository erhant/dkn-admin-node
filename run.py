import logging
import threading
from typing import Dict, Type

from run_aggregator import Aggregator
from run_monitor import Monitor
from run_publisher import Publisher
from src.config import Config

config = Config()
logger = logging.getLogger(__name__)


def thread_function(task_instance):
    """Run the given task instance in a separate thread."""
    try:
        task_instance.run()
    except Exception as e:
        logger.error(f"Error occurred in {type(task_instance).__name__}: {e}")


def main():
    """
    Run all tasks in separate threads.

    config.AGGREGATOR_WORKERS: Number of aggregator workers to run.
    config.MONITORING_WORKERS: Number of monitoring workers to run.
    config.PUBLISHER_WORKERS: Number of publisher workers to run.
    """
    tasks: Dict[Type, int] = {
        Aggregator: config.aggregator_workers,
        Monitor: config.monitoring_workers,
        Publisher: config.publisher_workers,
    }

    threads = []

    for task_class, num_workers in tasks.items():
        for _ in range(num_workers):
            task_instance = task_class(config)
            thread = threading.Thread(target=thread_function, args=(task_instance,))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

    logger.info("All tasks completed.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    main()
