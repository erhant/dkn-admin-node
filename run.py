import logging
import threading
from typing import Dict, Type, Union

from src.functions import Monitor, Publisher, Aggregator
from src.config import Config

config = Config()
logger = logging.getLogger(__name__)


def thread_function(task_instance: Union[Monitor, Publisher, Aggregator]):
    """
    Run the given task instance in a separate thread.

    :param task_instance: The task instance to run.
    """
    try:
        task_instance.run()
    except Exception as e:
        logger.error(f"Error occurred in {type(task_instance).__name__}: {e}", exc_info=True)


def main():
    """
    Run all tasks in separate threads.

    config.AGGREGATOR_WORKERS: Number of aggregator workers to run.
    config.MONITORING_WORKERS: Number of monitoring workers to run.
    config.PUBLISHER_WORKERS: Number of publisher workers to run.
    """
    print("Starting tasks...")
    print(config.monitoring_workers, config.aggregator_workers, config.publisher_workers)
    tasks: Dict[Type[Union[Monitor, Publisher, Aggregator]], int] = {
        Aggregator: config.aggregator_workers,
        Monitor: config.monitoring_workers,
        Publisher: config.publisher_workers,
    }

    threads = []

    for task_class, num_workers in tasks.items():
        for _ in range(num_workers):
            try:
                task_instance = task_class(config)
            except Exception as e:
                logger.error(f"Error creating instance of {task_class.__name__}: {e}", exc_info=True)
                continue
            thread = threading.Thread(target=thread_function, args=(task_instance,))
            threads.append(thread)
            thread.start()

    for thread in threads:
        try:
            thread.join()
        except Exception as e:
            logger.error(f"Error joining thread: {e}", exc_info=True)

    logger.info("All tasks completed.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    try:
        main()
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
