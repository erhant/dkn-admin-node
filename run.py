import threading

from run_aggregator import Aggregator
from run_monitor import Monitor
from run_publisher import Publisher
from src.config import Config

config = Config()


def thread_function(obj):
    obj.run()


if __name__ == "__main__":
    """
    Run all tasks in separate threads.
    
    config.AGGREGATOR_WORKERS: Number of aggregator workers to run.
    config.MONITORING_WORKERS: Number of monitoring workers to run.
    config.PUBLISHER_WORKERS: Number of publisher workers to run.
    
    """
    tasks = {
        Aggregator: config.AGGREGATOR_WORKERS,
       Monitor: config.MONITORING_WORKERS,
        Publisher: config.PUBLISHER_WORKERS,
    }

    threads = []

    for task_class, num_workers in tasks.items():
        for _ in range(num_workers):
            task_instance = task_class()
            thread = threading.Thread(target=thread_function, args=(task_instance,))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

    print("All tasks completed.")
