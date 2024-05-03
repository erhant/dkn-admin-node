import json
import logging
from typing import Dict, List, Union

logger = logging.getLogger(__name__)


def resolve_tasks(task_data: Dict[str, Union[str, List[Dict]]]) -> List[Dict]:
    """
    Resolve tasks from the task data.

    :param task_data: A dictionary containing the task data.
    :return: List of tasks.
    :raises ValueError: If the task data is not a dictionary or does not contain a 'tasks' key.
    :raises TypeError: If the tasks cannot be loaded as JSON or if the 'filter' key is missing from any task.
    """
    if not isinstance(task_data, dict):
        raise ValueError("Invalid task data format. Expected a dictionary.")

    if "tasks" not in task_data:
        raise ValueError("Task data does not contain a 'tasks' key.")

    try:
        tasks = task_data["tasks"]
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"Error decoding tasks: {e}")
        raise TypeError("Error decoding tasks.") from e

    resolved_tasks = []
    for task in tasks:
        if not isinstance(task, dict):
            logger.warning(f"Skipping invalid task: {task}")
            continue

        if "filter" not in task:
            logger.warning(f"Skipping task without 'filter' key: {task}")
            continue

        filter_data = task["filter"]
        if not isinstance(filter_data, dict):
            logger.warning(f"Skipping task with invalid 'filter' data: {filter_data}")
            continue

        if "hex" not in filter_data:
            logger.warning(f"Skipping task without 'hex' key in 'filter': {filter_data}")
            continue

        hex_value = filter_data["hex"]
        if isinstance(hex_value, bytes):
            filter_data["hex"] = bytes.fromhex(hex_value)
        elif isinstance(hex_value, str):
            try:
                filter_data["hex"] = hex_value.encode("utf-8")
            except UnicodeEncodeError as e:
                logger.warning(f"Skipping task with invalid 'hex' value: {hex_value}. Error: {e}")
                continue
        else:
            logger.warning(f"Skipping task with invalid 'hex' type: {type(hex_value)}")
            continue

        resolved_tasks.append(task)

    return resolved_tasks
